import subprocess
import RPi.GPIO as GPIO
import time
import readchar

def set_pins_high(pins):
    for pin in pins:
        GPIO.output(pin, GPIO.HIGH)
    print(f"Pins {pins} set to HIGH")

def set_pins_low(pins):
    for pin in pins:
        GPIO.output(pin, GPIO.LOW)
    print(f"Pins {pins} set to LOW")

def vibrate_motor(pin, duration=0.2):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

def handle_key_input(key, pins_dict):
    if key == '\x1b[A':  # Up arrow
        vibrate_motor(pins_dict['up'])  # Pin 16
    elif key == '\x1b[B':  # Down arrow
        vibrate_motor(pins_dict['down'])  # Pin 13
    elif key == '\x1b[D':  # Left arrow
        vibrate_motor(pins_dict['left'])  # Pin 26
    elif key == '\x1b[C':  # Right arrow
        vibrate_motor(pins_dict['right'])  # Pin 21
    elif key == '\x1b[A\x1b[D':  # Up + Left
        vibrate_motor(pins_dict['left_up'])  # Pin 19
    elif key == '\x1b[A\x1b[C':  # Up + Right
        vibrate_motor(pins_dict['right_up'])  # Pin 20

def monitor_and_control():
    # Setup GPIO
    pins = [26, 16, 20, 21, 13, 19]
    pins_dict = {
        'left': 26,
        'up': 16,
        'right_up': 20,
        'right': 21,
        'down': 13,
        'left_up': 19
    }
    
    GPIO.setmode(GPIO.BCM)
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Ensure pins start LOW

    try:
        object_detected_count = 0
        nothing_detected_count = 0
        pins_are_high = False
        target_output = "close objects detected in Camera"
        nothing_output = "nothing"

        # Run Arducam Demo and monitor output
        process = subprocess.Popen(['sudo', './run_Arducam_Demo'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        for line in process.stdout:
            line = line.strip()
            
            if line == target_output:
                object_detected_count += 1
                nothing_detected_count = 0
            elif line == nothing_output:
                nothing_detected_count += 1
                object_detected_count = 0
            else:
                object_detected_count = 0
                nothing_detected_count = 0

            # Set pins high after 2 consecutive object detections
            if object_detected_count == 2 and not pins_are_high:
                set_pins_high(pins)
                pins_are_high = True
                object_detected_count = 0

            # Set pins low after 2 consecutive "nothing" detections
            if nothing_detected_count == 2 and pins_are_high:
                set_pins_low(pins)
                pins_are_high = False
                nothing_detected_count = 0
                
                # After setting pins low, enter keyboard control mode
                print("Entering keyboard control mode. Press 'q' to exit.")
                while True:
                    key = readchar.readkey()
                    if key == 'q':
                        break
                    handle_key_input(key, pins_dict)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    monitor_and_control()

