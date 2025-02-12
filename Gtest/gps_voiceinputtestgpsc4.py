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
        instruction = step["html_instructions"]
        distance = step["distance"]["text"]
        print(f"SoleMate: {instruction} ({distance})")
        speak(f"{instruction} ({distance})")
        
        start_time = time.time()
        while True:
            new_location = get_gps_location()
            if new_location:
                distance_to_next = calculate_distance(new_location, current_location)
                if distance_to_next < 10:  # Assume user is at the step location
                    print("SoleMate: Step completed. Proceeding to the next instruction.")
                    speak("Step completed. Proceeding to the next instruction.")
                    break
            
            if time.time() - start_time > 30:
                print("SoleMate: No significant movement detected. Continuing navigation.")
                speak("No significant movement detected. Continuing navigation.")
                break
            
            time.sleep(1)

        current_location = new_location or current_location

def main():
    global current_location
    print("SoleMate: Please state your destination.")
    speak("Please state your destination.")
    destination_input = recognize_destination()

    if destination_input:
        place_info = search_place(destination_input)
        if place_info:
            print(f"SoleMate: Destination set to {place_info['name']}, {place_info['address']}.")
            speak(f"Destination set to {place_info['name']}, {place_info['address']}.")

            destination_coords = place_info["coordinates"]
            route_steps = get_directions(current_location, destination_coords)

            if route_steps:
                print("SoleMate: Starting real-time navigation.")
                speak("Starting real-time navigation.")
                navigate_route(route_steps)
            else:
                print("SoleMate: Unable to fetch route directions.")
                speak("Unable to fetch route directions.")
        else:
            print("SoleMate: Unable to set the destination.")
            speak("Unable to set the destination.")
    else:
        print("SoleMate: No destination provided.")
        speak("No destination provided.")

if __name__ == "__main__":
    main()
