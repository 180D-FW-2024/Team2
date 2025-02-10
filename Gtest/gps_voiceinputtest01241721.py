import googlemaps
from speech_recognition import Recognizer, Microphone
import pyttsx3
import time
from geopy.distance import geodesic
import gpsd

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

def recognize_command():
    recognizer = Recognizer()
    with Microphone() as source:
        print("SoleMate: Listening for a command...")
        try:
            audio = recognizer.listen(source, timeout=10)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except Exception as e:
            print(f"SoleMate: Could not recognize command. Error: {e}")
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
        
        # Monitor for voice commands during navigation
        while True:
            command = recognize_command()
            if command:
                if "change location to" in command.lower():
                    # Extract new destination from command
                    new_destination = command.lower().replace("change location to", "").strip()
                    print(f"SoleMate: Changing destination to {new_destination}")
                    speak(f"Changing destination to {new_destination}")
                    return new_destination  # Exit navigation with the new destination
                elif "stop navigation" in command.lower():
                    print("SoleMate: Stopping navigation.")
                    speak("Navigation stopped. Thank you for using SoleMate.")
                    return "STOP"

            # Check distance to the next step
            new_location = get_gps_location()  # Update current GPS location
            if new_location is None:
                continue
            distance_to_next = calculate_distance(new_location, current_location)
            if distance_to_next < 10:  # Assume 10 ft threshold for reaching the next step
                break
            time.sleep(1)

        current_location = new_location  # Update for the next step

def main():
    global current_location

    # Get initial GPS location
    print("GPS connected. Fetching initial location...")
    speak("GPS connected. Fetching initial location...")
    current_location = get_gps_location()
    if not current_location:
        print("SoleMate: Unable to fetch GPS location.")
        speak("Unable to fetch GPS location.")
        return

    print(f"Current location: {current_location}")

    while True:
        # Step 1: Get destination via voice
        destination_input = recognize_command()
        if destination_input:
            # Step 2: Search for the destination
            place_info = search_place(destination_input)
            if place_info:
                print(f"SoleMate: Destination set to {place_info['name']}, {place_info['address']}.")
                speak(f"Destination set to {place_info['name']}, {place_info['address']}.")

                # Step 3: Get directions to the destination
                destination_coords = place_info["coordinates"]
                while True:
                    route_steps = get_directions(current_location, destination_coords)

                    if route_steps:
                        print("SoleMate: Starting real-time navigation.")
                        speak("Starting real-time navigation.")
                        command = navigate_route(route_steps)

                        if command == "STOP":
                            return
                        elif isinstance(command, str):
                            # Update with new destination
                            destination_input = command
                            break
            else:
                print("SoleMate: Unable to set the destination.")
                speak("Unable to set the destination.")
        else:
            print("SoleMate: No destination provided.")
            speak("No destination provided.")

if __name__ == "__main__":
    main()
