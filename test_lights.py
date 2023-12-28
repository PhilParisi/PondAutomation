# this script is for testing the lights exclusively
# this script can only be run on a raspberryPi

import RPi.GPIO as GPIO
import time
from configs.rpi_connections import rpi_connections
from functions.pond_functions import *

# setup GPIO Pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(rpi_connections["red_LED"],GPIO.OUT)
GPIO.setup(rpi_connections["blue_LED"],GPIO.OUT)
GPIO.setup(rpi_connections["green_LED"],GPIO.OUT)


# 5 loops of each light
print('turning each light on sequentially 5 times')
print('the lights on should match the output in the terminal')

try: 
    for i in range(5):
        GPIO.output(rpi_connections["red_LED"],GPIO.HIGH)
        print('red on')
        time.sleep(1)
        GPIO.output(rpi_connections["red_LED"],GPIO.LOW)
        GPIO.output(rpi_connections["blue_LED"],GPIO.HIGH)
        print('blue on')
        time.sleep(1)
        GPIO.output(rpi_connections["blue_LED"],GPIO.LOW)
        GPIO.output(rpi_connections["green_LED"],GPIO.HIGH)
        print('green on')
        time.sleep(1)
        GPIO.output(rpi_connections["green_LED"],GPIO.LOW)
        
    
except KeyboardInterrupt:
    shutdown_lights(rpi_connections)
    print('done')