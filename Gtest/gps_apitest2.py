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
API_KEY = "xxxxxxx"  # Replace with valid Google Maps API key
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

    # Step 5: Display clean directions
    if directions:
        print("Turn-by-Turn Navigation Instructions:")
        for step in directions[0]["legs"][0]["steps"]:
            # Use BeautifulSoup to clean HTML tags from instructions
            clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
            distance = step["distance"]["text"]  # Extract the distance for the step
            print(f"{clean_instruction} ({distance})")

            # Add logic for traffic lights if present in the API response
            # Traffic light detection is not directly supported by Google Maps API.
            # You might need a separate API for this or process points of interest.
    else:
        print("No directions found. Please check your input data.")
except googlemaps.exceptions.ApiError as e:
    print(f"Google Maps API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
