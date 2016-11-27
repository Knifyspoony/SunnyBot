#!/usr/bin/python

import wiringpi
from time import sleep


LED  = 1 # gpio pin 12 = wiringpi no. 1 (BCM 18)
LED2 = 23 # gpio pin 33 = wiringpi no. 23 (BCM 13)


# Initialize PWM output for LED
wiringpi.wiringPiSetup()
wiringpi.pinMode(LED, 2)     # PWM mode
wiringpi.pinMode(LED2, 2)
wiringpi.pwmWrite(LED, 0)    # OFF
wiringpi.pwmWrite(LED2, 0)

# Set LED brightness
def led(led_value):
    wiringpi.pwmWrite(LED,led_value)
    wiringpi.pwmWrite(LED2,1024-led_value)

#wiringpi.pwmWrite(LED,100)

while True:
    for value in range(0,1024):
        led(value)
        sleep(0.001)
