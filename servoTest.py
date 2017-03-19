#!/usr/bin/python
"""Servo test
Using software PWM at 50Hz, control the Tower Pro SG90 microservo
7% duty cycle = -90 degrees (anti-clockwise)
16% duty cycle = 0 degrees
25% duty cycle = +90 degrees (clockwise)
"""


import wiringpi
from time import sleep

OUTPUT = 1

PIN_TO_PWM = 15 #wiringpi pin 15 = gpio 8

wiringpi.wiringPiSetup()
wiringpi.pinMode(PIN_TO_PWM,OUTPUT)
wiringpi.softPwmCreate(PIN_TO_PWM,0,50) # Setup PWM using Pin, Initial Value and Range parameters

for time in range(0,1):
	for duty in [7, 16, 24]: # Going from 7 to 25 will give us 90 degrees left to 90 degrees right
		wiringpi.softPwmWrite(PIN_TO_PWM,duty) # Change PWM duty cycle
		print(duty)
		sleep(1) # Delay for 0.2 seconds
	for duty in [24, 16, 7]:
		wiringpi.softPwmWrite(PIN_TO_PWM,duty)
		print(duty)
		sleep(1)
