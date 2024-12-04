import googlemaps

# Initialize the Google Maps client
API_KEY = "API key"  #  API key
gmaps = googlemaps.Client(key=API_KEY)

# Function to get directions
def get_directions(origin, destination):
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="walking"  # Use "driving", "bicycling", or "transit" if needed
    )
    # Parse the response to get steps
    for step in directions_result[0]['legs'][0]['steps']:
        print(f"Instruction: {step['html_instructions']}")
        print(f"Distance: {step['distance']['text']}")
        print(f"Duration: {step['duration']['text']}")
        print()

# Function to get distance and duration
def get_distance_and_time(origin, destination):
    distance_result = gmaps.distance_matrix(origin, destination, mode="walking")
    distance = distance_result['rows'][0]['elements'][0]['distance']['text']
    duration = distance_result['rows'][0]['elements'][0]['duration']['text']
    print(f"Distance: {distance}, Duration: {duration}")

# Test the functions
if __name__ == "__main__":
    origin = "Times Square, New York, NY"
    destination = "Central Park, New York, NY"
    print("Fetching directions...")
    get_directions(origin, destination)
    print("Fetching distance and duration...")
    get_distance_and_time(origin, destination)
