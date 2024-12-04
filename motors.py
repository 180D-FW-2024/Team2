# Raspberry Pi Pico

from machine import Pin
import time

# Motors 1-6
M1 = Pin(10, Pin.OUT) # W 
M2 = Pin(11, Pin.OUT) # NW
M3 = Pin(12, Pin.OUT) # N / front
M4 = Pin(14, Pin.OUT) # NE
M5 = Pin(15, Pin.OUT) # E
M6 = Pin(16, Pin.OUT) # S / back

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
