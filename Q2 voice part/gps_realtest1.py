import googlemaps
import gpsd
import pyttsx3
import time
from geopy.distance import geodesic
from bs4 import BeautifulSoup  # To clean instructions

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize Google Maps API
API_KEY = "xxx"
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

# Function to parse and give instructions
def parse_and_announce(directions):
    for step in directions[0]["legs"][0]["steps"]:
        instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
        distance = step["distance"]["text"]
        speak(f"{instruction}. In {distance}.")
        print(f"{instruction} ({distance})")
        time.sleep(2)

# Function to monitor GPS and update navigation
def start_navigation(destination_address):
    gpsd.connect()
    print("GPS connected. Fetching initial location...")
    try:
        while True:
            # Fetch real-time GPS location
            gps_data = gpsd.get_current()
            user_location = (gps_data.lat, gps_data.lon)

            # Fetch updated directions
            origin = f"{gps_data.lat},{gps_data.lon}"
            directions = fetch_directions(origin, destination_address)

            if directions:
                parse_and_announce(directions)

                # Monitor next step dynamically
                for step in directions[0]["legs"][0]["steps"]:
                    next_coords = (
                        step["start_location"]["lat"],
                        step["start_location"]["lng"],
                    )
                    while geodesic(user_location, next_coords).meters > 5:
                        # Update real-time GPS
                        gps_data = gpsd.get_current()
                        user_location = (gps_data.lat, gps_data.lon)
                        time.sleep(1)
            else:
                print("Failed to fetch directions. Retrying...")
                time.sleep(5)
    except KeyboardInterrupt:
        print("Navigation stopped.")
        speak("Navigation stopped.")
    except Exception as e:
        print(f"Error during navigation: {e}")
        speak("An error occurred during navigation.")

# Main Script
if __name__ == "__main__":
    destination = "UCLA Bookstore, Los Angeles, CA, USA"
    speak("Starting real-time navigation.")
    start_navigation(destination)
