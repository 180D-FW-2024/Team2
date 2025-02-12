import googlemaps
import gpsd
import pyttsx3
import time
from geopy.distance import geodesic
from bs4 import BeautifulSoup
import speech_recognition as sr

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize Google Maps API
API_KEY = "xxxxxxx"
gmaps = googlemaps.Client(key=API_KEY)

# Function to fetch directions
def fetch_directions(origin, destination):
    try:
        directions = gmaps.directions(
            origin=origin,
            destination=destination,
            mode="walking"  # or "driving"
        )
        return directions
    except Exception as e:
        print(f"Error fetching directions: {e}")
        return None

# Function to parse directions
def parse_directions(directions):
    steps = []
    for step in directions[0]["legs"][0]["steps"]:
        instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
        distance = step["distance"]["text"]
        location = (
            step["end_location"]["lat"],
            step["end_location"]["lng"]
        )
        steps.append({"instruction": instruction, "distance": distance, "location": location})
    return steps

# Function to recognize voice for destination
def recognize_destination():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("SoleMate: Please state your destination.")
        speak("Please state your destination.")
        try:
            audio = recognizer.listen(source, timeout=10)
            destination = recognizer.recognize_google(audio)
            print(f"You said: {destination}")
            return destination
        except sr.UnknownValueError:
            print("SoleMate: Sorry, I could not understand your destination.")
            speak("Sorry, I could not understand your destination.")
        except sr.RequestError as e:
            print(f"SoleMate: Could not request results; {e}")
            speak(f"Could not request results; {e}")
        return None

# Function to monitor and announce steps dynamically
def monitor_and_announce(steps):
    gpsd.connect()
    print("GPS connected. Fetching initial location...")
    try:
        for step in steps:
            while True:
                gps_data = gpsd.get_current()
                current_position = (gps_data.lat, gps_data.lon)
                distance_to_next = geodesic(current_position, step["location"]).meters

                if distance_to_next < 10:  # Threshold for reaching waypoint
                    print(f"{step['instruction']} ({step['distance']})")
                    speak(f"{step['instruction']}. {step['distance']}.")
                    break  # Move to the next step

                time.sleep(2)  # Adjust update frequency
    except KeyboardInterrupt:
        print("Navigation stopped.")
        speak("Navigation stopped.")
    except Exception as e:
        print(f"Error during navigation: {e}")
        speak("An error occurred during navigation.")

# Main Script
if __name__ == "__main__":
    gpsd.connect()
    gps_data = gpsd.get_current()
    origin = f"{gps_data.lat},{gps_data.lon}"
    
    destination = recognize_destination()  # Get destination via voice
    if destination:
        try:
            # Geocode to validate and get full location
            geocode_result = gmaps.geocode(destination)
            if geocode_result:
                full_destination = geocode_result[0]["formatted_address"]
                print(f"SoleMate: Destination set to {full_destination}.")
                speak(f"Destination set to {full_destination}.")
                
                directions = fetch_directions(origin, full_destination)
                if directions:
                    steps = parse_directions(directions)
                    speak("Starting real-time navigation.")
                    monitor_and_announce(steps)
                else:
                    speak("Failed to fetch directions.")
            else:
                print("SoleMate: Unable to find the destination.")
                speak("Unable to find the destination.")
        except Exception as e:
            print(f"Error processing destination: {e}")
            speak("An error occurred while processing the destination.")
    else:
        print("SoleMate: No destination provided.")
        speak("No destination provided.")
