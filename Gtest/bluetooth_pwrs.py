import bluetooth

# Create a Bluetooth socket
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Search for devices
print("Scanning for devices...")
devices = bluetooth.discover_devices(duration=8, lookup_names=True)
for addr, name in devices:
    print(f"Found device: {name} [{addr}]")
    if name == "Your_Pico_W_Name":  # Replace with your Pico W's Bluetooth name
        target_addr = addr

# Connect to the Pico W
if target_addr:
    print(f"Connecting to {target_addr}...")
    sock.connect((target_addr, 1))
    print("Connected!")

    # Send data to the Pico W
    sock.send("Hello Pico W!")

    # Receive response from Pico W
    response = sock.recv(1024).decode('utf-8')
    print("Received:", response)

    # Close the connection
    sock.close()
else:
    print("Pico W not found.")
