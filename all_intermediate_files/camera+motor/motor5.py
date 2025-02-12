import subprocess
import RPi.GPIO as GPIO
import time
import readchar
import select
import sys

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
        vibrate_motor(pins_dict['up'])
    elif key == '\x1b[B':  # Down arrow
        print("Down arrow pressed - activating lower motor")
        vibrate_motor(pins_dict['down'])
    elif key == '\x1b[D':  # Left arrow
        print("Left arrow pressed - activating left motor")
        vibrate_motor(pins_dict['left'])
    elif key == '\x1b[C':  # Right arrow
        print("Right arrow pressed - activating right motor")
        vibrate_motor(pins_dict['right'])
    elif key == ',':
        print("Comma pressed - activating upper-left motor")
        vibrate_motor(pins_dict['left_up'])
    elif key == '.':
        print("Period pressed - activating upper-right motor")
        vibrate_motor(pins_dict['right_up'])

def monitor_and_control():
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
        GPIO.output(pin, GPIO.LOW)

    try:
        process = subprocess.Popen(['sudo', './run_Arducam_Demo'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        object_detected_count = 0
        nothing_detected_count = 0
        obstacle_mode = False
        print("\n=== Keyboard Control Mode Active ===")

        while True:
            # Check for camera output
            if process.stdout in select.select([process.stdout], [], [], 0)[0]:
                line = process.stdout.readline().strip()
                
                if line == "close objects detected in Camera":
                    object_detected_count += 1
                    nothing_detected_count = 0
                    print("Camera output: obstacle")
                elif line == "nothing detected, good to go!":
                    nothing_detected_count += 1
                    object_detected_count = 0
                    print("Camera output: nothing")

                if object_detected_count >= 3 and not obstacle_mode:
                    print("Obstacle detected! Activating all motors")
                    set_pins_high(pins)
                    time.sleep(1)
                    set_pins_low(pins)
                    obstacle_mode = True
                    object_detected_count = 0
                elif nothing_detected_count >= 3 and obstacle_mode:
                    print("Path clear - returning to keyboard control")
                    obstacle_mode = False
                    nothing_detected_count = 0

            # Check for keyboard input
            if not obstacle_mode and select.select([sys.stdin], [], [], 0)[0]:
                key = readchar.readkey()
                if key == 'q':
                    print("Exiting program...")
                    break
                handle_key_input(key, pins_dict)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        process.terminate()
        GPIO.cleanup()
        print("Program terminated")

if __name__ == "__main__":
    print("Starting SoleMate motor control program...")
    monitor_and_control()

