
"""Script for using pygame to read in playstation dual shock 4 controller
with ds4drv  running as a daemon. Controller used to drive SunnyBot using
differential steering calculated using a proportional controller.
Also servo control of a tower pro SG90 servo on the right stick.
DS4  controller axis maps:
Axis0: Left stick l-r (-1 left, 1 right)
Axis1: Left stick u-d (-1 up, 1 down)
Axis2: Left trigger (-1 unpressed, 1 completely pressed)
Axis3: Right stick l-r (-1 left, 1 right)
Axis4: Right stick u-d (-1 up, 1 down)
Axis5: Right trigger (-1 unpressed, 1 completely pressed)

Button13: UP
Button14: DOWN

Servo info:
7% duty cycle = -90 degrees (anti-clockwise)
16% duty cycle = 0 degrees
25% duty cycle = +90 degrees (clockwise) makes some odd sounds though limit to 24

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

ServoPWM = 15 #gpio pin 8 = wiringpi no. 15 (BCM 14)

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

wiringpi.pinMode(ServoPWM,1) #output for software PWM
wiringpi.softPwmCreate(ServoPWM,16,50) #50Hz softpwm starting at mid position 

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
duty = 16 #default servo duty cycle for upright position

while True:
    pygame.event.get()   
    rt = joy.get_axis(5) #right trigger
    lt = joy.get_axis(2) #left trigger
    ls = joy.get_axis(0) #left stick left-right
    rs = joy.get_axis(4) #right stick up-down
    up = joy.get_button(13) #up on the D pad
    down = joy.get_button(14) #down on the D pad

    baseSpeed = (rt+1)/2 #convert +/-1 to 0-1
    if baseSpeed <= 0.01: #if right trigger isn't pulled
        baseSpeed = (lt+1)/2
        if baseSpeed <= 0.01: #if neither trigger is pulled
            sensitivity = 1.0 #allow spinning on the spot if no trigger is being pulled
            direction = 1.0 #forward
        else:    #if left trigger is pulled
            sensitivity = 0.5 #normal steering
            direction = -1.0 #backward
    else: #if right trigger is pulled
        sensitivity = 0.5 #normal steering
        direction = 1.0 #forward       
#   motor speed balance
    mlb = ls*sensitivity		#how speed is balanced across motors
    mrb = mlb*-1.0
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

    #servo control
    #duty = (((rs+1)/2)*17)+7 #convert -1 to 1 into 0-1 then multiply up to 0-17, add constant for 7-24
    if(up):
        duty += 1
    elif(down):
        duty -= 1

    if duty < 7:
        duty = 7
    elif duty > 24:
        duty = 24

    wiringpi.softPwmWrite(ServoPWM, duty)
    print('Duty: ', str(duty))
    sleep(0.1) #limit the frequency to 10Hz
