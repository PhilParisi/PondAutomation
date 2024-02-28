# this script is for opening the solenoid (flood) exclusively
# this script can only be run on a raspberryPi
# keep in mind the solenoid won't flow without a bit of pressure (blowing heavily can simulate flow)
# pay attention to the arrow on the top of the solenoid for the direction of flow

# wiring guide
    # + end from the wall outlet should go into the NC
    # a wire should connect the COM to one of the solenoid terminals
    # GND from the wall outlet should go to the other solenoid terminal 

import time
import smbus
import RPi.GPIO as GPIO
from configs.rpi_connections import rpi_connections
from functions.pond_functions import *

# setup GPIO Pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(rpi_connections["red_LED"],GPIO.OUT)
GPIO.setup(rpi_connections["blue_LED"],GPIO.OUT)
GPIO.setup(rpi_connections["green_LED"],GPIO.OUT)

# setup relay device variables
device_bus = 1 #this is set with the physical switches on the relay, 1 is default)
relay_addr = 0x10 #this is the number of the relay to actuate (0x10, 0x20, 0x30, or 0x40)
bus = smbus.SMBus(device_bus)

print('sending commands to open the solenoid once')
print('if you want to close the solenoid, run the "close_solenoid.py" script or shut off the RPi. Do this before running the autopond.')
print('Warning: leaving the solenoid open (turned on with voltage running thru it) for a few hours may result in overheating. Close the solenoid if solenoid is too hot to touch.')

try: 

    # turn ON (0xFF is 256 max), open solenoid
    bus.write_byte_data(relay_addr, device_bus, 0xFF)
    print("solenoid open")

    # turn on blue light only to indicate flood
    GPIO.output(rpi_connections["blue_LED"],GPIO.HIGH)  # turn on
    GPIO.output(rpi_connections["red_LED"],GPIO.LOW)    # turn off
    GPIO.output(rpi_connections["green_LED"],GPIO.LOW)  # turn off
    print("blue light on")
    


except KeyboardInterrupt:
        
        # turn OFF (0x00 is 0 min)
        bus.write_byte_data(relay_addr, device_bus, 0x00)
        print("solenoid closed")
    
        GPIO.output(rpi_connections["blue_LED"],GPIO.LOW)   # turn off
        GPIO.output(rpi_connections["red_LED"],GPIO.LOW)    # turn off
        GPIO.output(rpi_connections["green_LED"],GPIO.LOW)  # turn off
        print('lights off')
        print('script done')