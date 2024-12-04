# Raspberry Pi (temp)

from gpiozero import DigitalOutputDevice
import time

# Motors 1-6
M1 = DigitalOutputDevice(33)  # W 
M2 = DigitalOutputDevice(35)  # NW
M3 = DigitalOutputDevice(36)  # N / front
M4 = DigitalOutputDevice(37)  # NE
M5 = DigitalOutputDevice(38)  # E
M6 = DigitalOutputDevice(40)  # S / back

# Motor Functions
def stop_all():
    for motor in [M1, M2, M3, M4, M5, M6]:
        motor.off()

# Directions
def stop(duration):
    for motor in [M1, M2, M3, M4, M5, M6]:
        motor.on()
        time.sleep(duration)
        motor.off()

def move_forward(duration):
    M3.on()
    time.sleep(duration)
    M3.off()

def turn_left(duration):
    M1.on()
    M2.on()
    time.sleep(duration)
    M1.off()
    M2.off()

def turn_right(duration):
    M4.on()
    M5.on()
    time.sleep(duration)
    M4.off()
    M5.off()

def main():
    print("Testing all motors...")
    
    # Test individual motors
    for motor in [M1, M2, M3, M4, M5, M6]:
        print(f"Testing motor on pin {motor.pin.number}")
        motor.on()
        time.sleep(1)
        motor.off()
        time.sleep(0.5)
    
    # Test directional functions
    print("Testing forward movement")
    move_forward(2)
    time.sleep(1)
    
    print("Testing left turn")
    turn_left(2)
    time.sleep(1)
    
    print("Testing right turn")
    turn_right(2)
    time.sleep(1)
    
    print("Testing stop function")
    stop(2)
    
    print("Motor test complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        stop_all()
        print("All motors stopped")
