import time
from geopy.distance import geodesic
from haversine import haversine
from geopy.geocoders import Nominatim
from googlemaps import Client as GoogleMapsClient
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"SoleMate: Error in text-to-speech: {e}")

# Initialize geolocator
geolocator = Nominatim(user_agent="solemate")

# Initialize Google Maps API
API_KEY = "xxxxxxx"  # Replace with your API key
gmaps = GoogleMapsClient(key=API_KEY)

def get_current_gps_coordinates():
    # Simulated GPS polling logic, replace with actual GPS module code
    return (34.0689, -118.4452)

def get_route_instructions(origin, destination):
    try:
        directions = gmaps.directions(origin, destination, mode="walking")
        if not directions:
            return None

        steps = []
        for step in directions[0]['legs'][0]['steps']:
            instructions = step['html_instructions']
            distance = step['distance']['text']
            steps.append(f"{instructions} ({distance})")
        return steps
    except Exception as e:
        print(f"SoleMate: Error fetching route: {e}")
        return None

def narrate_full_route(steps):
    if not steps:
        print("SoleMate: No route steps found to narrate.")
        speak("I couldn't find any steps for this route.")
        return

    print("SoleMate: Here is your full route:")
    speak("Here is your full route.")

    for step in steps:
        print(f"SoleMate: {step}")
        speak(step)
        time.sleep(2)  # Ensure TTS completes before continuing to the next step

def start_real_time_navigation(origin, destination):
    try:
        steps = get_route_instructions(origin, destination)
        if not steps:
            print("SoleMate: Unable to retrieve navigation steps.")
            speak("I couldn't retrieve the navigation steps.")
            return

        narrate_full_route(steps)

        print("SoleMate: Starting real-time navigation.")
        speak("Starting real-time navigation.")

        current_step_index = 0
        while current_step_index < len(steps):
            current_location = get_current_gps_coordinates()
            next_instruction = steps[current_step_index]
            print(f"SoleMate: {next_instruction}")
            speak(next_instruction)
            current_step_index += 1
            time.sleep(5)  # Simulate delay for real-time navigation
    except Exception as e:
        print(f"SoleMate: Error during navigation: {e}")
        speak("An error occurred during navigation.")

def get_destination_from_user():
    print("SoleMate: Please state your destination.")
    speak("Please state your destination.")
    destination = input("Enter your destination: ")  # Replace with voice input logic
    return destination

def main():
    print("Starting SoleMate real-time navigation...")
    speak("Starting SoleMate real-time navigation.")

    origin = get_current_gps_coordinates()
    print(f"Starting location: {origin}")

    while True:
        destination_name = get_destination_from_user()
        try:
            geocode_result = gmaps.geocode(destination_name)
            if geocode_result:
                destination = geocode_result[0]['formatted_address']
                print(f"SoleMate: Destination set to {destination}.")
                speak(f"Destination set to {destination}.")
                start_real_time_navigation(origin, destination)
            else:
                print("SoleMate: Unable to find the destination.")
                speak("I couldn't find the destination. Please try again.")
        except Exception as e:
            print(f"SoleMate: Error searching for destination: {e}")
            speak("An error occurred while searching for the destination.")

if __name__ == "__main__":
    main()
