from time import sleep
import sys
import numpy as np
import QTR8A

# instantiate the line sensors
line_sensors = QTR8A.QTR8A()
# check the reset calibration function works (not necessary)
line_sensors.reset_calibration()
# read in the raw values to check the sensors are working
values = line_sensors.read_raw()
print(values)
# start the calibration sequence for 5 seconds - print the results
line_sensors.calibrate(5)
print(line_sensors.calibrated_max)
print(line_sensors.calibrated_min)
# read in the sensor values with calibration
values = line_sensors.read_calibrated()
print(values)
# continuously run the read line function

while True:
    line = line_sensors.read_line()
    print(line)
    sleep(1)    
