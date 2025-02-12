import socket
import time

server_ip = '192.168.0.117' 
server_port = 65432

while True:
    try:
        s = socket.socket()
        s.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")
        
        message = "Hello from Pico W!"
        s.send(message.encode())
        
        response = s.recv(1024)
        print(f"Received: {response.decode()}")
        
        s.close()
        time.sleep(5)  # Wait for 5 seconds before sending the next message
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Wait before retrying

