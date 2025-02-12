import bluetooth

def setup_bluetooth_server():
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)

    print("Waiting for connection...")
    client_socket, address = server_socket.accept()
    print(f"Connected to {address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
            client_socket.send("Data received".encode('utf-8'))
    except OSError:
        pass

    print("Connection closed")
    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    setup_bluetooth_server()
