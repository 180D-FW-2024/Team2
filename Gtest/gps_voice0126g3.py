import time
import pyttsx3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import googlemaps
import threading

# Initialize TTS engine
engine = pyttsx3.init()

# Google Maps API client
gmaps = googlemaps.Client(key="xxxxxxxU")

# Function to speak text
def speak(text):
    print(f"SoleMate: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to get the full route
def get_full_route(origin, destination):
    directions_result = gmaps.directions(origin, destination, mode="walking")
    if directions_result:
        steps = directions_result[0]['legs'][0]['steps']
        route = []
        for step in steps:
            instruction = step['html_instructions']
            distance = step['distance']['text']
            route.append(f"{instruction} ({distance})")
        return route
    return None

def get_gps_location():
    try:
        gpsd.connect()
        packet = gpsd.get_current()
        if packet.mode >= 2:  # Ensure we have a valid fix
            return (packet.lat, packet.lon)
        else:
            print("SoleMate: No GPS fix available.")
            speak("No GPS fix available.")
            return None
    except Exception as e:
        print(f"SoleMate: Error accessing GPS module: {e}")
        speak("Error accessing GPS module.")
        return None


# Function to start navigation
def start_navigation(origin, destination):
    directions_result = gmaps.directions(origin, destination, mode="walking")
    if directions_result:
        steps = directions_result[0]['legs'][0]['steps']
        for step in steps:
            instruction = step['html_instructions']
            distance = step['distance']['text']
            speak(f"{instruction} ({distance})")
            print(f"SoleMate: {instruction} ({distance})")
            time.sleep(5)  # Simulate time for user to walk
    speak("You have reached your destination. Thank you for using SoleMate!")

# Main function to handle navigation
def main():
    geolocator = Nominatim(user_agent="solemate")

    # Get current GPS coordinates
    origin_coords = get_gps_location()
    origin = f"{origin_coords[0]}, {origin_coords[1]}"

    speak("Please state your destination.")
    destination = input("Enter your destination (e.g., Whole Foods): ")

    # Geocode the destination
destination_geocode = gmaps.geocode(destination)
    if destination_geocode:
        destination_coords = destination_geocode[0]['geometry']['location']
        destination_address = destination_geocode[0]['formatted_address']

        # Fetch the full route
        route = get_full_route(origin, destination_address)
        if route:
            speak("Here is your full route:")
            for step in route:
                speak(step)
                print(f"SoleMate: {step}")
            speak("Starting real-time navigation.")

            # Start real-time navigation
            start_navigation(origin, destination_address)
        else:
            speak("Unable to fetch the route. Please try again.")
    else:
        speak("Unable to find the destination. Please try again.")

if __name__ == "__main__":
    main()
