import googlemaps
import gpsd
from bs4 import BeautifulSoup  # For cleaning HTML tags

# Step 1: Connect to gpsd
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
API_KEY = "xxxx"  # Replace with valid Google Maps API key
client = googlemaps.Client(key=API_KEY)

# Step 3: Define origin and destination
origin = f"{latitude},{longitude}"  # Dynamic GPS input
destination = "UCLA Bookstore, Los Angeles, CA, USA"  # Destination address

# Step 4: Get directions using Google Maps Directions API
try:
    directions = client.directions(
        origin=origin,
        destination=destination,
        mode="walking"  # Walking mode
    )

    # Step 5: Display navigation and control motor
    if directions:
        print("Turn-by-Turn Navigation Instructions:")
        for step in directions[0]["legs"][0]["steps"]:
            # Clean HTML tags from instructions
            clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
            distance = step["distance"]["text"]  # Extract step distance
            
            # Determine motor control output
            if "left" in clean_instruction.lower():
                motor_output = 2  # Left turn
            elif "right" in clean_instruction.lower():
                motor_output = 4  # Right turn
            else:
                motor_output = 0  # Continue forward or other action
            
            # Print and send motor control command
            print(f"{clean_instruction} ({distance}) → Motor Output: {motor_output}")

    else:
        print("No directions found. Please check your input data.")
except googlemaps.exceptions.ApiError as e:
    print(f"Google Maps API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
