# Import Google Maps Python Client
import googlemaps
from speech_recognition import Recognizer, Microphone
import pyttsx3

# Initialize Google Maps API Client
API_KEY = "xxxxxxx"
gmaps = googlemaps.Client(key=API_KEY)

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize voice for destination
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

# Function to search for places using the Places API
def search_place(query):
    try:
        places_result = gmaps.places(query=query)
        if places_result and places_result["status"] == "OK":
            # Use the first result
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

# Main Function
if __name__ == "__main__":
    # Step 1: Get the destination via voice
    destination_input = recognize_destination()
    if destination_input:
        # Step 2: Use Places API to find the destination
        place_info = search_place(destination_input)
        if place_info:
            print(f"SoleMate: Destination set to {place_info['name']}, {place_info['address']}.")
            speak(f"Destination set to {place_info['name']}, {place_info['address']}.")
        else:
            print("SoleMate: Unable to set the destination.")
    else:
        print("SoleMate: No destination provided.")
        speak("No destination provided.")
