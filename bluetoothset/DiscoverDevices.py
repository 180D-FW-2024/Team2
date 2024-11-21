val bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
if (bluetoothAdapter == null) {
    Toast.makeText(this, "Bluetooth not supported", Toast.LENGTH_SHORT).show()
} else if (!bluetoothAdapter.isEnabled) {
    val enableBtIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
    startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT)
}

val pairedDevices: Set<BluetoothDevice> = bluetoothAdapter.bondedDevices
for (device in pairedDevices) {
    Log.d("Bluetooth", "Device: ${device.name}, ${device.address}")
}
