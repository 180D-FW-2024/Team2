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
    print(f"Vibrating motor on pin {pin}")
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

def handle_key_input(key, pins_dict):
    if key == '\x1b[A':  # Up arrow
        print("Up arrow pressed - activating upper motor")
        vibrate_motor(pins_dict['up'])  # Pin 16
    elif key == '\x1b[B':  # Down arrow
        print("Down arrow pressed - activating lower motor")
        vibrate_motor(pins_dict['down'])  # Pin 13
    elif key == '\x1b[D':  # Left arrow
        print("Left arrow pressed - activating left motor")
        vibrate_motor(pins_dict['left'])  # Pin 26
    elif key == '\x1b[C':  # Right arrow
        print("Right arrow pressed - activating right motor")
        vibrate_motor(pins_dict['right'])  # Pin 21
    elif key == '\x1b[A\x1b[D':  # Up + Left
        print("Up + Left arrows pressed - activating upper-left motor")
        vibrate_motor(pins_dict['left_up'])  # Pin 19
    elif key == '\x1b[A\x1b[C':  # Up + Right
        print("Up + Right arrows pressed - activating upper-right motor")
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
    
    print("Initializing GPIO pins...")
    GPIO.setmode(GPIO.BCM)
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Ensure pins start LOW
    print("GPIO initialization complete")

    try:
        object_detected_count = 0
        nothing_detected_count = 0
        pins_are_high = False
        target_output = "close objects detected in Camera"
        nothing_output = "nothing detected, good to go!"

        print("Starting Arducam Demo monitoring...")
        # Run Arducam Demo and monitor output
        process = subprocess.Popen(['sudo', './run_Arducam_Demo'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        print("Monitoring camera output...")
        for line in process.stdout:
            line = line.strip()
            print(f"Camera output: {line}")
            
            if line == target_output:
                object_detected_count += 1
                nothing_detected_count = 0
                print(f"Object detected! Count: {object_detected_count}")
            elif line == nothing_output:
                nothing_detected_count += 1
                object_detected_count = 0
                print(f"Nothing detected! Count: {nothing_detected_count}")
            else:
                object_detected_count = 0
                nothing_detected_count = 0

            # Set pins high after 2 consecutive object detections
            if object_detected_count == 2 and not pins_are_high:
                print("Two consecutive objects detected - activating all motors")
                set_pins_high(pins)
                pins_are_high = True
                object_detected_count = 0

            # Set pins low after 2 consecutive "nothing" detections
            if nothing_detected_count == 2 and pins_are_high:
                print("Two consecutive 'nothing' detections - deactivating motors")
                set_pins_low(pins)
                pins_are_high = False
                nothing_detected_count = 0
                
                # After setting pins low, enter keyboard control mode
                print("\n=== Entering Keyboard Control Mode ===")
                print("Use arrow keys to control motors:")
                print("?: Upper motor")
                print("?: Lower motor")
                print("?: Left motor")
                print("?: Right motor")
                print("?+?: Upper-left motor")
                print("?+?: Upper-right motor")
                print("Press 'q' to exit")
                print("=====================================\n")
                
                while True:
                    key = readchar.readkey()
                    if key == 'q':
                        print("Exiting keyboard control mode...")
                        break
                    handle_key_input(key, pins_dict)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("Cleaning up GPIO...")
        GPIO.cleanup()
        print("Program terminated")

if __name__ == "__main__":
    print("Starting SoleMate motor control program...")
    monitor_and_control()

