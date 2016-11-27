#!/usr/bin/python

import wiringpi
from time import sleep


Motor1PWM  = 1 # gpio pin 12 = wiringpi no. 1 (BCM 18)
Motor1AIN1 = 4 # gpio pin 16 = wiringpi no. 4 (BCM 23)
Motor1AIN2 = 5 # gpio pin 18 = wiringpi no. 5 (BCM 24)
MotorStandby = 6 # gpio pin 22 = wiringpi no. 6 (BCM 25)

# Initialize PWM output
wiringpi.wiringPiSetup()
wiringpi.pinMode(Motor1PWM, 2)     # PWM mode
wiringpi.pinMode(Motor1AIN1, 1) #Digital out mode
wiringpi.pinMode(Motor1AIN2, 1) #Digital out mode
wiringpi.pinMode(MotorStandby, 1) #Ditial out mode

wiringpi.pwmWrite(Motor1PWM, 0)    # OFF
wiringpi.digitalWrite(Motor1AIN1, 1) #forward mode
wiringpi.digitalWrite(Motor1AIN2, 0) #forward mode
wiringpi.digitalWrite(MotorStandby, 1) #enabled


# Set LED brightness
def motorspeed(speed_value):
    wiringpi.pwmWrite(Motor1PWM, speed_value)

while True:
    for value in range(0,1024):
        motorspeed(value)
        sleep(0.1)
        print(value)
    for value in range(1024,0,-1):
        motorspeed(value)
        sleep(0.01)
        print(value)

