import spidev
from time import sleep
import sys
import numpy as np

class QTR8A:

    #constructor
    def __init__(self):
        self.num_sensors = 8
        self.calibrated_max = np.zeros(self.num_sensors)
        self.calibrated_min = np.zeros(self.num_sensors)
        self.not_calibrated = True
        self.spi = spidev.SpiDev()
        self.spi.open(0,0) #SPI bus 0, device 0
        self.spi.max_speed_hz = 1000000 # max speed of 1MHz

    # calibrate the sensors, taking in the duration of calibration in seconds
    def calibrate(self, duration=1):
        # do a cycle every 100ms
        num_cycles = duration*10
        # start by resetting the calibration
        self.reset_calibration()
        # create a blank array for storing the values
        values = np.zeros([num_cycles, self.num_sensors])
        # check the sensor values for the defined duration
        for i in range(0,num_cycles):
            # store values for each sensor and each cycle
            values[i,:] = self.read_raw()
            # wait before running the next check
            sleep(0.1)
        # check the read in values for maximums and minimums
        # an individual set is stored for each sensor
        for i in range(0,self.num_sensors):
            max = np.max(values[:,i])
            min = np.min(values[:,i])
            # update the maximum and minimum
            self.calibrated_max[i] = max
            self.calibrated_min[i] = min
        # set flag for calibration
        self.not_calibrated = False                

    # reset the calibration
    def reset_calibration(self):
        self.calibrated_max = np.zeros(self.num_sensors)
        self.calibrated_min = np.zeros(self.num_sensors)
        self.not_calibrated = True

    # read all 8 channels of the MCP3008 for the 8 different qtr sensors
    def read_raw(self):
        line = np.zeros(self.num_sensors)    
        for i in range(0,self.num_sensors):
            r = self.spi.xfer2([1,(8+i)<<4,0])
            line[i] = ((r[1]&3) << 8) + r[2]
        return line

    # read the line sensors but return values calibrated
    # values between 0-1000 where 0 is white surface, 1000 is black surface
    def read_calibrated(self):
        # if not calibrated, do nothing
        if(self.not_calibrated==True):
            return -1 
        raw_values = self.read_raw()
        for i in range(0, self.num_sensors):
            # make sure that the raw values are within min/max range
            if(raw_values[i] < self.calibrated_min[i]):
                raw_values[i] = self.calibrated_min[i]
            elif(raw_values[i] > self.calibrated_max[i]):
                raw_values[i] = self.calibrated_max[i]
        # scale the raw values between 0 and 1000    
        calibrated_values = (raw_values - self.calibrated_min)*(1000/(self.calibrated_max - self.calibrated_min))
        return calibrated_values

    # reads calibrated line sensor values and looks for a black line on white background
    # returns a value from 0 to 1000
    # optimised for a 15mm wide line
    def read_line(self):
        # read in the calibrated sensor values
        values = self.read_calibrated()
        # store the max value and where it is in the array
        max = np.max(values)
        index = np.argmax(values)
        # define the calibration constant
        k = 1000/(self.num_sensors-1)
        # check the max sensor against the sensors either side
        # calculate a representative 0-1000 number for the line position
        if index == 0:
            offset = values[index+1]/(max*2)
            line = (index + offset)*k
        elif index == self.num_sensors-1:
            offset = -1*values[index-1]/(max*2)
            line = (index + offset)*k
        else:
            offset = (-1*values[index-1] + values[index+1])/(max*2)
            line = (index + offset)*k
        return line

