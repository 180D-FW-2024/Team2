val device = bluetoothAdapter.getRemoteDevice(macAddress)
val socket = device.createRfcommSocketToServiceRecord(uuid)
socket.connect()

val outputStream = socket.outputStream
val inputStream = socket.inputStream

// Send a message
outputStream.write("Hello from Android!".toByteArray())

// Receive a message
val buffer = ByteArray(1024)
val bytes = inputStream.read(buffer)
val receivedMessage = String(buffer, 0, bytes)
Log.d("Bluetooth", "Message received: $receivedMessage")
