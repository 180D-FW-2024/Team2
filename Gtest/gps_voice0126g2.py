import time
import gpsd
import pyttsx3
import googlemaps
from haversine import haversine

# Google Maps API Key (replace with your API key)
API_KEY = "xxxxxxx"
gmaps = googlemaps.Client(key=API_KEY)

# Text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

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

def get_navigation_directions(start_coords, end_coords):
    try:
        directions_result = gmaps.directions(
            origin=start_coords,
            destination=end_coords,
            mode="walking"
        )
        if directions_result:
            return directions_result[0]['legs'][0]['steps']
        else:
            return None
    except Exception as e:
        print(f"SoleMate: Error fetching directions: {e}")
        speak("Error fetching directions.")
        return None

def haversine_distance(coord1, coord2):
    """Calculate the distance between two GPS coordinates in meters."""
    return haversine(coord1, coord2) * 1000

def start_navigation(destination_coords):
    print("SoleMate: Starting real-time navigation.")
    speak("Starting real-time navigation.")

    while True:
        current_coords = get_gps_location()
        if current_coords is None:
            time.sleep(2)
            continue

        directions = get_navigation_directions(current_coords, destination_coords)
        if not directions:
            print("SoleMate: Unable to get directions.")
            speak("Unable to get directions.")
            break

        for step in directions:
            print(f"SoleMate: {step['html_instructions']} ({step['distance']['text']})")
            speak(f"{step['html_instructions']} ({step['distance']['text']})")

            while True:
                updated_coords = get_gps_location()
                if updated_coords is None:
                    time.sleep(2)
                    continue

                if haversine_distance(updated_coords, step['end_location']['lat'], step['end_location']['lng']) < 10:
                    print("SoleMate: Step completed. Proceeding to the next instruction.")
                    speak("Step completed. Proceeding to the next instruction.")
                    break

        print("SoleMate: You have reached your destination.")
        speak("You have reached your destination.")
        break

def main():
    print("SoleMate: Please state your destination.")
    speak("Please state your destination.")

    destination = input("Enter your destination: ")
    try:
        geocode_result = gmaps.geocode(destination)
        if not geocode_result:
            print("SoleMate: Unable to find the destination.")
            speak("Unable to find the destination.")
            return

        destination_coords = (
            geocode_result[0]['geometry']['location']['lat'],
            geocode_result[0]['geometry']['location']['lng']
        )
        destination_address = geocode_result[0]['formatted_address']

        print(f"SoleMate: Destination set to {destination_address}.")
        speak(f"Destination set to {destination_address}.")

        start_navigation(destination_coords)

    except Exception as e:
        print(f"SoleMate: Error processing destination: {e}")
        speak("Error processing destination.")

if __name__ == "__main__":
    main()
