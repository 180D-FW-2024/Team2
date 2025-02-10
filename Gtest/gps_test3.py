import serial
import time
from geopy.distance import geodesic
import pyttsx3
import requests

GOOGLE_MAPS_API_KEY = "xxxxxxx"

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

def get_current_gps_coordinates():
    """Fetch real-time GPS coordinates from the GPS module."""
    try:
        gps_serial = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
        while True:
            gps_data = gps_serial.readline().decode('ascii', errors='replace').strip()
            if gps_data.startswith('$GNGGA'):
                fields = gps_data.split(',')
                if fields[2] and fields[4]:
                    latitude = convert_to_decimal(fields[2], fields[3])
                    longitude = convert_to_decimal(fields[4], fields[5])
                    return latitude, longitude
        return None, None
    except serial.SerialException as e:
        print(f"Error accessing GPS module: {e}")
        speak("Error accessing GPS module. Please check the device.")
        return None, None

def convert_to_decimal(value, direction):
    """Convert NMEA GPS coordinates to decimal degrees."""
    degrees = int(value[:2])
    minutes = float(value[2:])
    decimal = degrees + (minutes / 60)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_navigation_instructions(origin, destination):
    """Fetch navigation steps using Google Maps Directions API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin[0]},{origin[1]}",
        "destination": destination,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "walking",
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] != "OK":
            print(f"Error fetching navigation: {data['status']}")
            speak(f"Error fetching navigation: {data['status']}")
            return []

        steps = data["routes"][0]["legs"][0]["steps"]
        instructions = [step["html_instructions"] for step in steps]
        return [instruction.replace('<b>', '').replace('</b>', '') for instruction in instructions]
    except Exception as e:
        print(f"Error fetching navigation: {e}")
        speak("Error fetching navigation instructions.")
        return []

def main():
    print("Starting SoleMate real-time navigation...")
    speak("Starting SoleMate real-time navigation.")

    # Fetch the starting GPS coordinates
    current_coords = get_current_gps_coordinates()
    if not current_coords or current_coords == (None, None):
        print("Unable to fetch GPS data. Please check the module.")
        speak("Unable to fetch GPS data. Please check the module.")
        return

    print(f"Starting location: {current_coords}")
    speak("GPS connected. Fetching initial location.")

    # Get destination from user
    speak("Please say your destination.")
    destination = input("Enter your destination (e.g., UCLA Bookstore): ").strip()

    # Fetch navigation instructions dynamically
    instructions = get_navigation_instructions(current_coords, destination)

    if not instructions:
        print("Unable to fetch navigation instructions.")
        speak("Unable to fetch navigation instructions.")
        return

    for step in instructions:
        print(f"Instruction: {step}")
        speak(step)

        # Simulate waiting and fetching updated coordinates
        time.sleep(5)  # Wait 5 seconds to simulate user movement
        new_coords = get_current_gps_coordinates()

        if not new_coords or new_coords == (None, None):
            print("Lost GPS signal. Please ensure clear access to the sky.")
            speak("Lost GPS signal. Please ensure clear access to the sky.")
            continue

        print(f"Current location: {new_coords}")

    print("You have reached your destination.")
    speak("You have reached your destination.")

if __name__ == "__main__":
    main()
