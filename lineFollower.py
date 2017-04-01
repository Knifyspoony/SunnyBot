
"""Line following script with ds4 controller as supervisor
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
import numpy as np
import QTR8A


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

"""SPI pins for MCP3008:
SCLK->CLK gpio 23
MISO->DOUT gpio 21
MOSI->DIN gpio 19
CE0->CS gpio 24
"""

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

#initialise the line sensors
line_sensors = QTR8A.QTR8A()

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

motorspeed(0,0) #start with zero motor speed
base_speed = 0.25 #set base speed
Kp = 1.5
error = 0

while True:
    motorspeed(0,0) #turn the motors off!
    pygame.event.get()   #get pygame values for reading in ds4 buttons
    triangle = joy.get_button(3)
    cross = joy.get_button(0)
    square = joy.get_button(2)
    start = cross
    up = joy.get_button(13) #up on the D pad
    down = joy.get_button(14) #down on the D pad
#check for the calibrate button to get pressed
    if(triangle == 1):
        print('Calibration started')
        motorspeed(1.0, -1.0) #set the robot going in a circle
        line_sensors.calibrate(2) #calibrate for 2 seconds
        motorspeed(0,0) #stop the robot

#check for base_speed changes
    if(up):
        base_speed = base_speed + 0.05
        print('Base speed now: ' + str(base_speed))
        sleep(0.5)
    elif(down):
        base_speed = base_speed - 0.05
        print('Base speed now: ' + str(base_speed))
        sleep(0.5)

    if(start):
        print('Starting line following')

    #while go button is pressed
    while(start == 1):
#        print('Cross pressed')
        line_position = line_sensors.read_line() #read in the line sensor values
# calibrated values are between 0 and 1000. 0 is white surface, 1000 is black. Index 0 is right hand sensor, index 7 is left most
        line_values = line_sensors.read_calibrated()
        if(line_values[0] >= 900):
            error = -1.0
        elif(line_values[7] >= 900):
            error = 1.0 
        elif(line_position > 0):
            error = line_position/500 - 1.0 #line position is 0-1000, convert to -1 to 1
        else:
            error = error #keep the error the same
        print('Error is: ' + str(error))
        m1_speed = base_speed - Kp*error
        m2_speed = base_speed + Kp*error

        m1_overshoot = m1_speed - 1.0
        m2_overshoot = m2_speed - 1.0
        if(m1_overshoot <= 0):
            m1_overshoot = 0
        if(m2_overshoot <=0):
            m2_overshoot = 0

        m1_speed = m1_speed - m2_overshoot #carry over overly positive motor speeds
        m2_speed = m2_speed - m1_overshoot 

        if(m1_speed > 1.0):
            m1_speed = 1.0
        elif (m1_speed < -1.0):
            m1_speed = -1.0
        if(m2_speed > 1.0):
            m2_speed = 1.0
        elif (m2_speed < -1.0):
            m2_speed = -1.0
        motorspeed(m1_speed, m2_speed)
 #       print('Motor1 speed: ' + str(m1_speed) + ' Motor2 speed: ' + str(m2_speed))
        pygame.event.get()   #get pygame values for reading in ds4 buttons
        cross = joy.get_button(0)
        square = joy.get_button(2)
        if(square):
            start = 0 #stop if square is pressed
            print('Stopping line following')
        sleep(0.01)
