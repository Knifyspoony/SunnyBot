
"""Test script for using pygame to read in xbox 360 controller
with ds4drv  running as a daemon
DS4  controller axis maps:
Axis0: Left stick l-r (-1 left, 1 right)
Axis1: Left stick u-d (-1 up, 1 down)
Axis2: Left trigger (-1 unpressed, 1 completely pressed)
Axis3: Right stick l-r (-1 left, 1 right)
Axis4: Right stick u-d (-1 up, 1 down)
Axis5: Right trigger (-1 unpressed, 1 completely pressed)
"""

import pygame
import wiringpi
from time import sleep
import sys

#initialise DS4 controller
screen = pygame.display.set_mode([10,10]) #make a 10x10 window
pygame.joystick.init() #find the joysticks
joy = pygame.joystick.Joystick(0)
joy.init()
if(joy.get_name()=='Sony Entertainment Wireless Controller'):
    print("DS4 connected")
else:
    print("Not a DS4")


Motor1PWM  = 1 # gpio pin 12 = wiringpi no. 1 (BCM 18)
Motor1AIN1 = 4 # gpio pin 16 = wiringpi no. 4 (BCM 23)
Motor1AIN2 = 5 # gpio pin 18 = wiringpi no. 5 (BCM 24)
MotorStandby = 6 # gpio pin 22 = wiringpi no. 6 (BCM 25)
Motor2PWM = 23 # gpio pin 33 = wiringpi no. 23 (BCM 13)
Motor2BIN1 = 21 # gpio pin 29 = wiringpi no. 21 (BCM 5)
Motor2BIN2 = 22 # gpio pin 31 = wiringpi no. 22 (BCM 6)

# Initialize PWM output
wiringpi.wiringPiSetup()
wiringpi.pinMode(Motor1PWM, 2)     # PWM mode
wiringpi.pinMode(Motor1AIN1, 1) #Digital out mode
wiringpi.pinMode(Motor1AIN2, 1) #Digital out mode
wiringpi.pinMode(MotorStandby, 1) #Ditial out mode

wiringpi.pinMode(Motor2PWM, 2)     # PWM mode
wiringpi.pinMode(Motor2BIN1, 1)    #Digital out mode
wiringpi.pinMode(Motor2BIN2, 1)    #Digital out mode


wiringpi.pwmWrite(Motor1PWM, 0)    # OFF
wiringpi.pwmWrite(Motor2PWM, 0)    # OFF
wiringpi.digitalWrite(Motor1AIN1, 1) #forward mode
wiringpi.digitalWrite(Motor1AIN2, 0) #forward mode
wiringpi.digitalWrite(Motor2BIN1, 1)
wiringpi.digitalWrite(Motor2BIN2, 0)
wiringpi.digitalWrite(MotorStandby, 1) #enabled


# Set Motor Speed
def motorspeed(speed1, speed2):
    wiringpi.pwmWrite(Motor1PWM, speed1) #motorspeed from 0 to 1024
    wiringpi.pwmWrite(Motor2PWM, speed2) 

motorspeed(0,0) #start with 0 speed
while True:
    pygame.event.get()
#    for x in range(0,joy.get_numaxes()):
#        print('Axis'+str(x)+': '+str(joy.get_axis(x)))
   
    rt = joy.get_axis(5)
#    lt = joy.get_axis(2)
    ls = joy.get_axis(0)
    mlb = (ls+1)/2		#how speed is balanced across motors
    mrb = 1-mlb

#    left motor speed
    if mlb >= 0.5:
       ml = (rt+1)/2
    else:
       ml = 2*mlb*rt
    print(ml)

#    right motor speed
    if mrb >= 0.5:
       mr = (rt+1)/2
    else:
       mr = 2*mrb*rt
    print(mr)

#    print(rt)
#    print(lt)
#    print(ls)
#    print("Motor L balance value = ", mlb)
#    speed1 = (lt+1)*512
    speed1 = abs(ml*1024)

#    speed2 = (rt+1)*512
    speed2 = abs(mr*1024)
    motorspeed(int(speed1),int(speed2))
	
#    print(speed1)
    sleep(0.1) #limit the frequency to 10Hz
