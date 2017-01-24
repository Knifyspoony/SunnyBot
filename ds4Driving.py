
"""Test script for using pygame to read in playstation dual shock 4 controller
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
    print(joy.get_name())

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
    if speed1 < 0:
        wiringpi.digitalWrite(Motor1AIN1, 0) #reverse mode
        wiringpi.digitalWrite(Motor1AIN2, 1)
    else:
        wiringpi.digitalWrite(Motor1AIN1, 1) #forward mode
        wiringpi.digitalWrite(Motor1AIN2, 0)

    wiringpi.pwmWrite(Motor1PWM, int(abs(speed1)*1024)) #motorspeed from 0 to 1024

    if speed2 < 0:
        wiringpi.digitalWrite(Motor2BIN1, 0) #reverse mode
        wiringpi.digitalWrite(Motor2BIN2, 1)
    else:
        wiringpi.digitalWrite(Motor2BIN1, 1) #forward mode
        wiringpi.digitalWrite(Motor2BIN2, 0)

    wiringpi.pwmWrite(Motor2PWM, int(abs(speed2)*1024)) 

motorspeed(0,0) #start with 0 speed
rt = 0
sensitivity = 0.5 #define between 0 and 1 where 1 is most sensitive
direction = 1.0 # 1 for forward direction


while True:
    pygame.event.get()   
    rt = joy.get_axis(5)
#    print("rt: " + str(rt))
    lt = joy.get_axis(2)
    ls = joy.get_axis(0)
    mlb = ls*sensitivity		#how speed is balanced across motors
    mrb = mlb*-1.0
    baseSpeed = (rt+1)/2
    direction = 1.0 #forward
    if baseSpeed <= 0.01:
        baseSpeed = (lt+1)/2
        direction = -1.0 #backward       
#   motor speed balance
#   left motor speed
    ml = direction*(baseSpeed + mlb)
#   right motor speed 
    mr = direction*(baseSpeed + mrb)

    if ml > 1.0:
        ml = 1.0
    elif ml < -1.0:
        ml = -1.0
    if mr > 1.0:
        mr = 1.0
    elif mr < -1.0:
        mr = -1.0
    print("ml: " + str(ml) + " mr: " + str(mr))

    motorspeed(ml,mr)
    sleep(0.1) #limit the frequency to 10Hz
