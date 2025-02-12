import googlemaps
from speech_recognition import Recognizer, Microphone
import pyttsx3
import gpsd
import time
from bs4 import BeautifulSoup  # To clean instructions

# Initialize Google Maps API Client
API_KEY = "xxxxxxx"  # Replace 
gmaps = googlemaps.Client(key=API_KEY)

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    """ Speak out the given text """
    engine.say(text)
    engine.runAndWait()

def recognize_destination():
    """ Capture destination via voice input """
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
    """ Search for place coordinates using Google Maps Places API """
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
    """ Fetch walking directions between two locations """
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
    """ Get current GPS location """
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

def print_and_speak_directions(directions):
    """ Print and speak all navigation instructions immediately """
    if not directions:
        print("SoleMate: No navigation steps available.")
        speak("No navigation steps available.")
        return
    
    print("\nTurn-by-Turn Navigation Instructions:\n")
    speak("Here are the full navigation instructions.")

    for step in directions:
        clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
        distance = step["distance"]["text"]
        instruction_text = f"{clean_instruction} for {distance}"

        print(instruction_text)  # Print navigation step
        speak(instruction_text)  # Speak navigation step

        time.sleep(1)  # Short pause between instructions

def main():
    """ Main function to get user destination and provide full navigation steps """
    print("GPS connected. Fetching initial location...")
    speak("GPS connected. Fetching initial location.")

    current_location = get_gps_location()
    if not current_location:
        print("SoleMate: Unable to fetch GPS location.")
        speak("Unable to fetch GPS location.")
        return

    print(f"Current location: {current_location}")

    # Step 1: Get destination via voice
    destination_input = recognize_destination()
    if destination_input:
        if "stop navigation" in destination_input.lower():
            print("SoleMate: Navigation stopped. Thank you for using SoleMate.")
            speak("Navigation stopped. Thank you for using SoleMate.")
            return

        # Step 2: Search for the destination
        place_info = search_place(destination_input)
        if place_info:
            print(f"SoleMate: Destination set to {place_info['name']}, {place_info['address']}.")
            speak(f"Destination set to {place_info['name']}, {place_info['address']}.")

            # Step 3: Get directions to the destination
            destination_coords = place_info["coordinates"]
            route_steps = get_directions(current_location, destination_coords)

            if route_steps:
                print("SoleMate: Announcing full navigation instructions.")
                speak("Announcing full navigation instructions.")
                print_and_speak_directions(route_steps)  # Immediately speak all steps
            else:
                print("SoleMate: Unable to retrieve directions.")
                speak("Unable to retrieve directions.")
        else:
            print("SoleMate: Unable to set the destination.")
            speak("Unable to set the destination.")
    else:
        print("SoleMate: No destination provided.")
        speak("No destination provided.")

if __name__ == "__main__":
    main()
