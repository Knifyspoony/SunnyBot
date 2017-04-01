#!/usr/bin/python

import wiringpi

sun_led = 8 

wiringpi.pinMode(sun_led, 1) #Ditial out mode

wiringpi.digitalWrite(sun_led, 1) #enabled

