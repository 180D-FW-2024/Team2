import googlemaps
from speech_recognition import Recognizer, Microphone
import pyttsx3
import time
import threading
from geopy.distance import geodesic

# Initialize Google Maps API Client
API_KEY = "xxxxxxx"
gmaps = googlemaps.Client(key=API_KEY)

# Initialize Text-to-Speech
engine = pyttsx3.init()

# Global Variable for Current GPS Location
current_location = None

def speak(text):
    engine.say(text)
    engine.runAndWait()

def recognize_destination():
    recognizer = Recognizer()
    with Microphone() as source:
        print("SoleMate: Please state your destination.")
        speak("Please state your destination.")
        try:
            audio = recognizer.listen(source, timeout=10)
            destination = recognizer.recognize_google(audio)
            print(f"You said: {destination}")
            return destination
        except Exception as e:
            print(f"SoleMate: Could not recognize your destination. Error: {e}")
            speak("Could not recognize your destination.")
            return None

def search_place(query):
    try:
        places_result = gmaps.places(query=query)
        if places_result and places_result["status"] == "OK":
            place = places_result["results"][0]
            place_name = place["name"]
            place_address = place["formatted_address"]
            place_coordinates = place["geometry"]["location"]
            return {
                "name": place_name,
                "address": place_address,
                "coordinates": (place_coordinates["lat"], place_coordinates["lng"])
            }
        else:
            print("SoleMate: No places found.")
            speak("Unable to find the destination. Please try again.")
            return None
    except Exception as e:
        print(f"Error searching for place: {e}")
        speak("An error occurred while searching for the destination.")
        return None

def get_directions(start_coords, end_coords):
    try:
        directions_result = gmaps.directions(
            origin=start_coords,
            destination=end_coords,
            mode="walking"
        )
        if directions_result and directions_result[0]["legs"]:
            return directions_result[0]["legs"][0]["steps"]
        else:
            print("SoleMate: No directions found.")
            speak("Unable to retrieve directions.")
            return None
    except Exception as e:
        print(f"Error fetching directions: {e}")
        speak("An error occurred while retrieving directions.")
        return None

def get_gps_location():
    # Replace this with actual GPS code
    # Simulate GPS by returning fixed coordinates (e.g., UCLA coordinates)
    return (34.068921, -118.445181)

def calculate_distance(loc1, loc2):
    return geodesic(loc1, loc2).feet

def navigate_route(route_steps):
    global current_location
    for step in route_steps:
        # Extract step details
        instruction = step["html_instructions"]
        distance = step["distance"]["text"]
        print(f"SoleMate: {instruction} ({distance})")
        speak(f"{instruction} ({distance})")
        
        # Wait for user to move based on the distance
        while True:
            new_location = get_gps_location()  # Update current GPS location
            distance_to_next = calculate_distance(new_location, current_location)
            if distance_to_next < 10:  # Assume 10 ft threshold for reaching the next step
                break
            time.sleep(1)

        current_location = get_gps_location()  # Update for the next step

def main():
    global current_location

    # Get initial GPS location
    print("GPS connected. Fetching initial location...")
    speak("GPS connected. Fetching initial location...")
    current_location = get_gps_location()
    print(f"Current location: {current_location}")

    # Step 1: Get destination via voice
    destination_input = recognize_destination()
    if destination_input:
        # Step 2: Search for the destination
        place_info = search_place(destination_input)
        if place_info:
            print(f"SoleMate: Destination set to {place_info['name']}, {place_info['address']}.")
            speak(f"Destination set to {place_info['name']}, {place_info['address']}.")

            # Step 3: Get directions to the destination
            destination_coords = place_info["coordinates"]
            route_steps = get_directions(current_location, destination_coords)

            if route_steps:
                print("SoleMate: Starting real-time navigation.")
                speak("Starting real-time navigation.")
                navigate_route(route_steps)
        else:
            print("SoleMate: Unable to set the destination.")
    else:
        print("SoleMate: No destination provided.")
        speak("No destination provided.")

if __name__ == "__main__":
    main()
