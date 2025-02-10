import RPi.GPIO as GPIO
import googlemaps
import gpsd
from bs4 import BeautifulSoup  # For cleaning HTML tags
import time

# Motor GPIO Pin Definitions
LEFT_MOTOR = 17  # GPIO pin for left motor
RIGHT_MOTOR = 27  # GPIO pin for right motor

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR, GPIO.OUT)

# Step 1: Connect to GPS
try:
    gpsd.connect()
    gps_data = gpsd.get_current()
    latitude = gps_data.lat
    longitude = gps_data.lon

    if not latitude or not longitude:
        print("Invalid GPS data. Ensure the GPS module has a valid fix.")
        exit(1)
except Exception as e:
    print(f"Error connecting to GPS: {e}")
    exit(1)

# Step 2: Google Maps API Setup
API_KEY = "xxxxxxx "
client = googlemaps.Client(key=API_KEY)

# Step 3: Define origin and destination
origin = f"{latitude},{longitude}"  # Dynamic GPS input
destination = "UCLA Bookstore, Los Angeles, CA, USA"

# Step 4: Get directions using Google Maps API
try:
    directions = client.directions(
        origin=origin,
        destination=destination,
        mode="walking"
    )

    # Step 5: Process navigation and control motors
    if directions:
        print("Turn-by-Turn Navigation Instructions:")
        for step in directions[0]["legs"][0]["steps"]:
            clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
            distance = step["distance"]["text"]

            # Determine motor output
            if "left" in clean_instruction.lower():
                motor_output = 2  # Left turn
                GPIO.output(LEFT_MOTOR, GPIO.HIGH)  # Vibrate left motor
                time.sleep(0.5)  # Vibration duration
                GPIO.output(LEFT_MOTOR, GPIO.LOW)
            elif "right" in clean_instruction.lower():
                motor_output = 4  # Right turn
                GPIO.output(RIGHT_MOTOR, GPIO.HIGH)  # Vibrate right motor
                time.sleep(0.5)  # Vibration duration
                GPIO.output(RIGHT_MOTOR, GPIO.LOW)
            else:
                motor_output = 0  # No turn, no vibration

            print(f"{clean_instruction} ({distance}) → Motor Output: {motor_output}")

except googlemaps.exceptions.ApiError as e:
    print(f"Google Maps API Error: {e}")
except Exception as e:
    print(f"Error: {e}")

# Cleanup GPIO before exiting
GPIO.cleanup()
