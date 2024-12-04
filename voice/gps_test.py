import gpsd

# Connect to the local gpsd
gpsd.connect()

# Fetch the current GPS data
packet = gpsd.get_current()

if packet.mode >= 2:  # Check if we have a fix
    print(f"Latitude: {packet.lat}")
    print(f"Longitude: {packet.lon}")
    print(f"Altitude: {packet.alt} meters")
    print(f"Speed: {packet.speed()} m/s")
    print(f"Time: {packet.time}")
else:
    print("No GPS fix available.")
