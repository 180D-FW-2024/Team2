import googlemaps
import gpsd
from bs4 import BeautifulSoup  # Import to clean HTML tags

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
API_KEY = "API key"  # Replace api
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
        print("Directions to UCLA Bookstore:")
        for step in directions[0]["legs"][0]["steps"]:
            # Use BeautifulSoup to clean HTML tags
            clean_instruction = BeautifulSoup(step["html_instructions"], "html.parser").text
            print(clean_instruction)
    else:
        print("No directions found. Please check your input data.")
except googlemaps.exceptions.ApiError as e:
    print(f"Google Maps API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
