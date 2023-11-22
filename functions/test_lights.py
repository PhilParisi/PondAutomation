# this script is for testing the lights exclusively
# this script can only be run on a raspberryPi

import RPi.GPIO as GPIO
import time
from configs.rpi_connections import rpi_connections

# setup GPIO Pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(rpi_connections["red_LED"],GPIO.OUT)
GPIO.setup(rpi_connections["yellow_LED"],GPIO.OUT)
GPIO.setup(rpi_connections["green_LED"],GPIO.OUT)

# 5 loops
for i in range(5):
    GPIO.output(rpi_connections["red_LED"],GPIO.HIGH)
    time.sleep(1)
    GPIO.output(rpi_connections["red_LED"],GPIO.LOW)
    GPIO.output(rpi_connections["yellow_LED"],GPIO.HIGH)
    time.sleep(1)
    GPIO.output(rpi_connections["yellow_LED"],GPIO.LOW)
    GPIO.output(rpi_connections["green_LED"],GPIO.HIGH)
    time.sleep(1)
    GPIO.output(rpi_connections["green_LED"],GPIO.LOW)
    
    