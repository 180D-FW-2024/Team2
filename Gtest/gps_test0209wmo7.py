import time
import geopy.distance
from geopy.geocoders import Nominatim
from googlemaps import Client as GoogleMapsClient
import pyttsx3
import speech_recognition as sr
import gpsd

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    """Speak the given text."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"SoleMate: Error in text-to-speech: {e}")

# Initialize geolocator and Google Maps API
geolocator = Nominatim(user_agent="solemate")
API_KEY = "xxxxxxx-zU"  # Replace with API key
gmaps = GoogleMapsClient(key=API_KEY)

# Voice recognition setup
recognizer = sr.Recognizer()

def get_current_gps_coordinates():
    """Fetch real-time GPS coordinates from the GPS module."""
    try:
        gpsd.connect()  # Connect to the GPSD daemon
        packet = gpsd.get_current()
        if packet.mode >= 2:  # Ensure we have a valid GPS fix (2D or 3D)
            return (packet.lat, packet.lon)
        else:
            print("SoleMate: No GPS fix available.")
            return None
    except Exception as e:
        print(f"SoleMate: Error accessing GPS module: {e}")
        return None
    
def get_route_instructions(origin, destination):
    """Retrieve walking directions from Google Maps API."""
    try:
        directions = gmaps.directions(origin, destination, mode="walking")
        if not directions:
            return None

        steps = []
        for step in directions[0]['legs'][0]['steps']:
            instructions = step['html_instructions']
            distance = step['distance']['text']
            end_location = step['end_location']
            steps.append({
                "instruction": f"{instructions} ({distance})",
                "location": (end_location['lat'], end_location['lng'])
            })
        return steps
    except Exception as e:
        print(f"SoleMate: Error fetching route: {e}")
        speak("An error occurred while fetching the route.")
        return None

def narrate_full_route(steps):
    """Narrate the full route before real-time navigation starts."""
    if not steps:
        print("SoleMate: No route steps found.")
        speak("I couldn't find any steps for this route.")
        return False

    print("SoleMate: Here is your full route:")
    speak("Here is your full route.")

    for step in steps:
        print(f"SoleMate: {step['instruction']}")
        speak(step['instruction'])
        time.sleep(1)  # Small delay for natural narration
    return True

def start_real_time_navigation(origin, destination):
    """Begin real-time navigation with GPS updates."""
    steps = get_route_instructions(origin, destination)
    if not steps:
        print("SoleMate: Unable to retrieve navigation steps.")
        speak("I couldn't retrieve the navigation steps.")
        return

    if not narrate_full_route(steps):
        return

    print("SoleMate: Starting real-time navigation.")
    speak("Starting real-time navigation.")

    current_step_index = 0
    while current_step_index < len(steps):
        current_location = get_current_gps_coordinates()  # Fetch live GPS location
        next_step = steps[current_step_index]

        # Calculate distance between current location and next step
        step_location = next_step["location"]
        distance_to_next_step = geopy.distance.distance(current_location, step_location).meters

        if distance_to_next_step < 5:  # Threshold for reaching next step (5 meters)
            print(f"SoleMate: {next_step['instruction']}")
            speak(next_step['instruction'])
            current_step_index += 1
        else:
            print(f"SoleMate: Moving... {int(distance_to_next_step)} meters to next step")
        
        time.sleep(3)  # Update GPS data every 3 seconds

    print("SoleMate: You have arrived at your destination.")
    speak("You have arrived at your destination.")

def get_destination_from_user():
    """Listen for a destination name from voice input."""
    print("SoleMate: Please state your destination.")
    speak("Please state your destination.")
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for your destination...")
            audio = recognizer.listen(source)

        destination = recognizer.recognize_google(audio)
        print(f"You said: {destination}")
        return destination
    except sr.UnknownValueError:
        print("SoleMate: Sorry, I could not understand the destination.")
        speak("Sorry, I couldn't understand the destination. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"SoleMate: Error with voice recognition service: {e}")
        speak("There was an issue with the voice recognition service. Please try again.")
        return None

def main():
    print("Starting SoleMate real-time navigation...")
    speak("Starting SoleMate real-time navigation.")

    origin = get_current_gps_coordinates()
    print(f"Starting location: {origin}")

    while True:
        destination_name = get_destination_from_user()
        if not destination_name:
            continue

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
