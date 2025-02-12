import subprocess
import RPi.GPIO as GPIO
import time

def set_pin_high(pin):
    GPIO.output(pin, GPIO.HIGH)
    print(f"Pin {pin} set to HIGH")
    time.sleep(3)  # Keep pin high for 3 seconds
    GPIO.output(pin, GPIO.LOW)
    print(f"Pin {pin} set to LOW")

def monitor_and_control():
    # Setup GPIO
    pin = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Ensure pin starts LOW

    try:
        consecutive_count = 0
        target_output = "close objects detected in Camera"

        # Run Arducam Demo and monitor output
        process = subprocess.Popen(['sudo', './run_Arducam_Demo'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        for line in process.stdout:
            line = line.strip()
            if line == target_output:
                consecutive_count += 1
            else:
                consecutive_count = 0

            if consecutive_count == 3:
                set_pin_high(pin)
                consecutive_count = 0  # Reset count after triggering

    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    monitor_and_control()

