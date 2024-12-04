import pyttsx3
import speech_recognition as sr
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import gpsd
import time

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech.."""
    engine.say(text)
    engine.runAndWait()

wake_words = ["hello solemate", "hello soulmate", "hello solmate","hello s","hello"]

def is_wake_word(text):
    """Check if text contains any wake word."""
    for word in wake_words:
        if word in text.lower():
            return True
    return False

def recognize_voice():
    """Recognize voice commands."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a command...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I could not understand.")
            speak("Sorry, I could not understand.")
            return None
        except sr.RequestError:
            print("Could not request results; check your internet connection.")
            speak("Could not request results; check your internet connection.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            speak("Listening timed out.")
            return None

def connect_gps():
    """Connect to GPS module."""
    try:
        gpsd.connect()
        print("GPS connected successfully.")
        return True
    except Exception as e:
        print(f"Error connecting to GPS: {e}")
        speak("Unable to connect to GPS module.")
        return False

def get_gps_location():
    """Fetch current GPS location."""
    try:
        packet = gpsd.get_current()
        lat, lon = packet.lat, packet.lon
        print(f"GPS Location: Latitude {lat}, Longitude {lon}")
        return lat, lon
    except Exception as e:
        print(f"Error accessing GPS data: {e}")
        speak("Unable to fetch GPS data.")
        return None, None

def get_directions(origin, destination):
    """Get directions from origin to destination."""
    try:
        geolocator = Nominatim(user_agent="solemate")
        dest_location = geolocator.geocode(destination)
        if not dest_location:
            speak("Unable to find the destination.")
            return None

        dest_coords = (dest_location.latitude, dest_location.longitude)
        print(f"Destination Coordinates: {dest_coords}")

        # Example of directions simulation
        steps = [
            f"Head north for 100 meters.",
            f"Turn left toward {destination}.",
            f"Proceed to the destination.",
        ]
        return steps
    except Exception as e:
        print(f"Error getting directions: {e}")
        speak("Unable to fetch directions.")
        return None
    
def real_time_navigation(destination):
    """Provide real-time navigation updates."""
    while True:
        lat, lon = get_gps_location()
        if not lat or not lon:
            break
        print(f"Real-time position: Latitude {lat}, Longitude {lon}")
        speak(f"Current location: Latitude {lat}, Longitude {lon}")
        time.sleep(10)  # Adjust update interval

def main():
    """Main interactive loop."""
    if not connect_gps():
        return

    is_navigating = False
    destination = None

    speak("SoleMate is ready. Say 'Hello SoleMate' to begin.")

    while True:
        command = recognize_voice()
        if not command:
            continue

        if is_wake_word(command):
            speak("Hello! If there is anything I can help you with, just ask.")

        elif "navigate to" in command:
            destination = command.replace("navigate to", "").strip()
            speak(f"Getting directions to {destination}.")
            lat, lon = get_gps_location()
            if lat and lon:
                origin = f"{lat},{lon}"
                directions = get_directions(origin, destination)
                if directions:
                    speak("Starting navigation.")
                    is_navigating = True
                    for step in directions:
                        speak(step)
                        time.sleep(5)
                else:
                    speak("Could not retrieve directions. Please try again later.")
            else:
                speak("Unable to get current location.")

        elif "where am i" in command:
            lat, lon = get_gps_location()
            if lat and lon:
                speak(f"You are currently at latitude {lat} and longitude {lon}.")
            else:
                speak("Unable to get current location.")

        elif "change location to" in command:
            destination = command.replace("change location to", "").strip()
            speak(f"Updating destination to {destination}.")
            lat, lon = get_gps_location()
            if lat and lon:
                origin = f"{lat},{lon}"
                directions = get_directions(origin, destination)
                if directions:
                    speak("Starting updated navigation.")
                    for step in directions:
                        speak(step)
                        time.sleep(5)
                else:
                    speak("Could not retrieve directions. Please try again later.")
            else:
                speak("Unable to get current location.")

        elif "stop navigation" in command:
            is_navigating = False
            destination = None
            speak("Navigation stopped. Thank you for using SoleMate.")
            break

        else:
            speak("Command not recognized. Please try again.")

if __name__ == "__main__":
    main()
