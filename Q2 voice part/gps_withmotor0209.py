import googlemaps
import gpsd
import RPi.GPIO as GPIO
import time
import speech_recognition as sr
import pyttsx3
from bs4 import BeautifulSoup  # For cleaning HTML tags

# Motor GPIO Pin Definitions
LEFT_MOTOR = 17  # GPIO pin for left motor
RIGHT_MOTOR = 27  # GPIO pin for right motor

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR, GPIO.OUT)

# Initialize Speech Recognizer and Text-to-Speech
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)  # Adjust speech rate

# Function to speak text
def speak(text):
    print(f"SoleMate: {text}")  # Print text for debugging
    tts_engine.say(text)
    tts_engine.runAndWait()
    time.sleep(2)  # Extra delay after speaking the instruction

# Step 1: Connect to GPS
try:
    gpsd.connect()
    gps_data = gpsd.get_current()
    latitude = gps_data.lat
    longitude = gps_data.lon

    if not latitude or not longitude:
        speak("Invalid GPS data. Ensure the GPS module has a valid fix.")
        exit(1)
except Exception as e:
    speak(f"Error connecting to GPS: {e}")
    exit(1)

# Step 2: Google Maps API Setup
API_KEY = "xxxx"  # Replace with a valid Google Maps API key
client = googlemaps.Client(key=API_KEY)

# Step 3: Get Destination via Voice Input
def get_destination_from_voice():
    with sr.Microphone() as source:
        speak("Please say your destination.")
        time.sleep(1)  # Small delay before recording
        try:
            recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
            audio = recognizer.listen(source, timeout=10)
            destination = recognizer.recognize_google(audio)  # Convert speech to text
            speak(f"You said: {destination}")
            return destination
        except sr.UnknownValueError:
            speak("Could not understand the destination. Please try again.")
            return None
        except sr.RequestError:
            speak("Error with the voice recognition service. Please try again.")
            return None

# Get the destination via voice
destination = None
while destination is None:
    destination = get_destination_from_voice()

# Step 4: Get directions using Google Maps API
try:
    directions = client.directions(
        origin=f"{latitude},{longitude}",  
        destination=destination,
        mode="walking"
    )

    # Step 5: Process navigation and control motors
    if directions:
        speak("Turn-by-turn navigation started.")
        previous_instruction = ""

        for step in directions[0]["legs"][0]["steps"]:
            clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
            distance = step["distance"]["text"]

            # Determine motor control output
            if "left" in clean_instruction.lower():
                motor_output = 2  # Left turn
                GPIO.output(LEFT_MOTOR, GPIO.HIGH)  # Vibrate left motor
                time.sleep(0.5)  # Motor buzz duration
                GPIO.output(LEFT_MOTOR, GPIO.LOW)
            elif "right" in clean_instruction.lower():
                motor_output = 4  # Right turn
                GPIO.output(RIGHT_MOTOR, GPIO.HIGH)  # Vibrate right motor
                time.sleep(0.5)  # Motor buzz duration
                GPIO.output(RIGHT_MOTOR, GPIO.LOW)
            else:
                motor_output = 0  # No turn, no vibration

            # Speak and store previous instruction
            instruction_text = f"{clean_instruction} for {distance}."
            speak(instruction_text)

            previous_instruction = instruction_text  # Store previous step

            # Extra delay before next navigation step
            time.sleep(3)

            # Ask if the user wants to repeat the instruction
            with sr.Microphone() as source:
                speak("If you need me to repeat the last instruction, say 'repeat'. Otherwise, remain silent.")
                try:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=3)
                    command = recognizer.recognize_google(audio)

                    if "repeat" in command.lower():
                        speak(f"Repeating: {previous_instruction}")
                except:
                    pass  # No command detected, move to the next step

except googlemaps.exceptions.ApiError as e:
    speak(f"Google Maps API Error: {e}")
except Exception as e:
    speak(f"Error: {e}")

# Cleanup GPIO before exiting
GPIO.cleanup()
