import googlemaps
import gpsd
import pyttsx3
import time
from geopy.distance import geodesic
from bs4 import BeautifulSoup

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
    destination = "UCLA Bookstore, Los Angeles, CA, USA"
    gpsd.connect()
    gps_data = gpsd.get_current()
    origin = f"{gps_data.lat},{gps_data.lon}"
    directions = fetch_directions(origin, destination)

    if directions:
        steps = parse_directions(directions)
        speak("Starting real-time navigation.")
        monitor_and_announce(steps)
    else:
        speak("Failed to fetch directions.")
