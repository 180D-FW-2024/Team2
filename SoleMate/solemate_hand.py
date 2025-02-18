import socket
import googlemaps
import gpsd
import RPi.GPIO as GPIO
import time
import speech_recognition as sr
import pyttsx3
from bs4 import BeautifulSoup
from geopy.distance import geodesic
import math

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
tts_engine.setProperty("rate", 150)

# Minimum distance (in meters) before moving to the next step
THRESHOLD_DISTANCE = 5  
STOP_TIMEOUT = 10  # Time in seconds before reminding the user to keep moving

# Network details for sending to Raspberry Pi 2
server_ip = "192.168.0.117"  #  Raspberry Pi 2
server_port = 65432

def speak(text):
    print(f"SoleMate: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()
    time.sleep(2)

# Function to send navigation commands to Raspberry Pi 2
def send_command(command):
    try:
        s = socket.socket()
        s.connect((server_ip, server_port))
        s.send(command.encode())
        print(f"Sent: {command}")
        s.close()
    except Exception as e:
        print(f"Error sending command: {e}")


# Function to calculate bearing angle between two GPS points
def calculate_bearing(start, end):
    lat1, lon1 = math.radians(start[0]), math.radians(start[1])
    lat2, lon2 = math.radians(end[0]), math.radians(end[1])
    
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    initial_bearing = math.atan2(x, y)
    bearing_degrees = (math.degrees(initial_bearing) + 360) % 360  # Convert to 0-360°
    
    return bearing_degrees

# Function to convert bearing angle into a simple number
def get_numeric_direction(bearing):
    if 0 <= bearing < 45 or 315 <= bearing <= 360:
        return 0  # North
    elif 45 <= bearing < 135:
        return 90  # East
    elif 135 <= bearing < 225:
        return 180  # South
    elif 225 <= bearing < 315:
        return 270  # West
    else:
        return -1  # Error case

# Function to wait until the user reaches the next step
def wait_until_reach(destination_gps):
    last_movement_time = time.time()
    last_sent_direction = None  

    while True:
        gps_data = gpsd.get_current()
        current_gps = (gps_data.lat, gps_data.lon)
        distance_to_next = geodesic(current_gps, destination_gps).meters
        
        if distance_to_next <= 5:
            break  

        # Calculate the current bearing and direction
        bearing = calculate_bearing(previous_gps, current_gps)
        direction_number = get_numeric_direction(bearing)

        # Send direction only if it changes
        if direction_number != last_sent_direction:
            send_command(str(direction_number))
            last_sent_direction = direction_number

        if time.time() - last_movement_time > 10:
            speak("Keep going straight.")
            send_command(str(direction_number))  
            last_movement_time = time.time()
        
        time.sleep(2)  # Check every 2 seconds

# Step 1: Connect to GPS
gpsd.connect()
gps_data = gpsd.get_current()
latitude = gps_data.lat
longitude = gps_data.lon

if not latitude or not longitude:
    speak("Invalid GPS data. Ensure the GPS module has a valid fix.")
    exit(1)

# Step 2: Google Maps API Setup
API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Replace with a valid key
client = googlemaps.Client(key=API_KEY)

# Step 3: Get Destination via Voice Input
def get_destination_from_voice():
    with sr.Microphone() as source:
        speak("Please say your destination.")
        time.sleep(1)
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10)
            destination = recognizer.recognize_google(audio)
            speak(f"You said: {destination}")
            return destination
        except sr.UnknownValueError:
            speak("Could not understand the destination. Please try again.")
            return None
        except sr.RequestError:
            speak("Error with the voice recognition service. Please try again.")
            return None

destination = None
while destination is None:
    destination = get_destination_from_voice()

# Step 4: Get directions
directions = client.directions(
    origin=f"{latitude},{longitude}",  
    destination=destination,
    mode="walking"
)

# Process navigation
previous_gps = (latitude, longitude)
if directions:
    speak("Turn-by-turn navigation started.")
    previous_instruction = ""

    for step in directions[0]["legs"][0]["steps"]:
        clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
        distance = step["distance"]["text"]
        next_step_location = (step["end_location"]["lat"], step["end_location"]["lng"])

        speak(f"Walk {distance} {clean_instruction}.")
        send_command(f"Walk {distance} {clean_instruction}")

        wait_until_reach(next_step_location)
        
        gps_data = gpsd.get_current()
        current_gps = (gps_data.lat, gps_data.lon)
        bearing = calculate_bearing(previous_gps, current_gps)
        direction_number = get_numeric_direction(bearing)
        
        # Send numeric direction (0, 90, 180, 270)
        send_command(str(direction_number))

        previous_instruction = clean_instruction
        previous_gps = current_gps  
        time.sleep(1)    # Small delay before moving to the next instruction

        with sr.Microphone() as source:
            speak("If you need me to repeat the last instruction, say 'repeat'. Otherwise, remain silent.")
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=3)
                command = recognizer.recognize_google(audio)
                if "repeat" in command.lower():
                    speak(f"Repeating: {previous_instruction}")
            except:
                pass

GPIO.cleanup()