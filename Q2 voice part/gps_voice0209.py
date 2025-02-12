import googlemaps
from speech_recognition import Recognizer, Microphone
import pyttsx3
import time
from geopy.distance import geodesic
import gpsd
from bs4 import BeautifulSoup  # To clean instructions


# Initialize Google Maps API Client
API_KEY = "xxxx"
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

def parse_and_announce(directions):
    for step in directions[0]["legs"][0]["steps"]:
        instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
        distance = step["distance"]["text"]
        speak(f"{instruction}. In {distance}.")
        print(f"{instruction} ({distance})")
        time.sleep(1)

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


def navigate_route(route_steps):
    global current_location
    for step in route_steps:
        # Extract step details
        instruction = step["html_instructions"]
        distance = step["distance"]["text"]
        print(f"SoleMate: {instruction} ({distance})")
        speak(f"{instruction} ({distance})")
        
        # Wait for user to move based on the distance
        start_time = time.time()
        while True:
            new_location = get_gps_location()  # Update current GPS location
            if new_location is None:
                print("Waiting for GPS update...")
                time.sleep(1)
                continue
            
            distance_to_next = calculate_distance(new_location, current_location)
            if distance_to_next < 10:  # Assume 10 ft threshold for reaching the next step
                print(f"SoleMate: Step completed. Proceeding to the next instruction.")
                break
            
            # Timeout after 30 seconds of no progress
            if time.time() - start_time > 30:
                print("SoleMate: You seem stationary. Continuing with the next instruction.")
                speak("You seem stationary. Continuing with the next instruction.")
                break
            
            time.sleep(1)

        current_location = new_location  # Update for the next step


def main():
    global current_location

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
        destination_input = recognize_destination()
        if destination_input:
            if "stop navigation" in destination_input.lower():
                print("SoleMate: Navigation stopped. Thank you for using SoleMate.")
                speak("Navigation stopped. Thank you for using SoleMate.")
                break
            elif "change location to" in destination_input.lower():
                destination_input = destination_input.replace("change location to", "").strip()
            
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
                    destination = "UCLA Bookstore, Los Angeles, CA, USA"
                    speak("Starting real-time navigation.")
                    start_navigation(destination)
                    navigate_route(route_steps)
            else:
                print("SoleMate: Unable to set the destination.")
        else:
            print("SoleMate: No destination provided.")
            speak("No destination provided.")


if __name__ == "__main__":

    main()
