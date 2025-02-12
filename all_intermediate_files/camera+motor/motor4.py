import subprocess
import RPi.GPIO as GPIO
import time
import readchar
import threading

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

def camera_monitor(process, shared_state):
    object_detected_count = 0
    nothing_detected_count = 0
    target_output = "close objects detected in Camera"
    nothing_output = "nothing detected, good to go!"

    for line in process.stdout:
        line = line.strip()
        print(f"Camera output: {line}")

        if line == target_output:
            object_detected_count += 1
            nothing_detected_count = 0
            print(f"Camera output: obstacle ")
        elif line == nothing_output:
            nothing_detected_count += 1
            object_detected_count = 0
            print(f"Camera output: nothing ")
       # else:
       #     object_detected_count = 0
       #     nothing_detected_count = 0

        if object_detected_count >= 2:
            shared_state['obstacle_mode'] = True
            object_detected_count = 0
        elif nothing_detected_count >= 5:
            shared_state['obstacle_mode'] = False
            nothing_detected_count = 0

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

    shared_state = {'obstacle_mode': False}

    try:
        process = subprocess.Popen(['sudo', './run_Arducam_Demo'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        # Start camera monitoring in a separate thread
        camera_thread = threading.Thread(target=camera_monitor, 
                                       args=(process, shared_state))
        camera_thread.daemon = True
        camera_thread.start()

        print("\n=== Keyboard Control Mode Active ===")
        while True:
            if shared_state['obstacle_mode']:
                print("Obstacle detected! Activating all motors")
                set_pins_high(pins)
                time.sleep(1)
                set_pins_low(pins)
                while shared_state['obstacle_mode']:
                    time.sleep(0.1)
            else:
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

