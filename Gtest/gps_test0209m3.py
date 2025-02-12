import googlemaps
import gpsd
import speech_recognition as sr
import pyttsx3
from bs4 import BeautifulSoup  # For cleaning HTML tags
import json

# Initialize Text-to-Speech engine
tts = pyttsx3.init()
tts.setProperty("rate", 150)  # Adjust speech rate

# Step 1: Connect to GPS and get current location
try:
    gpsd.connect()
    gps_data = gpsd.get_current()
    latitude = gps_data.lat
    longitude = gps_data.lon

    if not latitude or not longitude:
        print("Invalid GPS data. Ensure the GPS module has a valid fix.")
        tts.say("Invalid GPS data. Ensure the GPS module has a valid fix.")
        tts.runAndWait()
        exit(1)

    print(f"Current GPS Location: {latitude}, {longitude}")
    
    tts.runAndWait()
except Exception as e:
    print(f"Error connecting to GPS: {e}")
    tts.say("Error connecting to GPS")
    tts.runAndWait()
    exit(1)

# Step 2: Get Destination via Voice Input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say your destination...")
        tts.say("Please say your destination")
        tts.runAndWait()

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        destination = recognizer.recognize_google(audio)
        print(f"Destination recognized: {destination}")
        tts.say(f"Navigating to {destination}")
        tts.runAndWait()
        return destination
    except sr.UnknownValueError:
        print("Could not understand the destination.")
        tts.say("Could not understand the destination. Please try again.")
        tts.runAndWait()
        exit(1)
    except sr.RequestError:
        print("Error with the voice recognition service.")
        tts.say("Error with the voice recognition service.")
        tts.runAndWait()
        exit(1)

destination = get_voice_input()

# Step 3: Google Maps API Setup
API_KEY = "xxxxxxx"  # Replace with a valid Google Maps API key
client = googlemaps.Client(key=API_KEY)

# Step 4: Get directions using Google Maps Directions API
try:
    directions = client.directions(
        origin=f"{latitude},{longitude}",  # GPS-based origin
        destination=destination,
        mode="walking"  # Walking mode
    )

    # Print the full API response for debugging
    print(json.dumps(directions, indent=4))

    # Step 5: Voice Output of Directions
    if directions:
        print("\nTurn-by-Turn Navigation Instructions:\n")
        tts.say("Here are the navigation instructions.")
        tts.runAndWait()

        # Extract navigation steps
        steps = directions[0]["legs"][0].get("steps", [])

        if not steps:
            print("No detailed steps found in the API response.")
            tts.say("No detailed steps found.")
            tts.runAndWait()
        else:
            for step in steps:
                clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
                distance = step["distance"]["text"]  # Extract step distance
                instruction_text = f"{clean_instruction} for {distance}"

                print(instruction_text)  # Print navigation step
                tts.say(instruction_text)  # Speak navigation step
                tts.runAndWait()

    else:
        print("No directions found. Please check your input data.")
        tts.say("No directions found. Please check your input.")
        tts.runAndWait()
except googlemaps.exceptions.ApiError as e:
    print(f"Google Maps API Error: {e}")
    tts.say("Google Maps API Error occurred.")
    tts.runAndWait()
except Exception as e:
    print(f"Error: {e}")
    tts.say("An error occurred while retrieving directions.")
    tts.runAndWait()
