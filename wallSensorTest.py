import spidev
from time import sleep
import sys

"""
wall sensors connected to MCP3008 channels 1, 4 and 7
Channel 1 -> Right hand view
Channel 4 -> Forward view
Channel 7 -> Left hand view
"""

spi = spidev.SpiDev()
spi.open(0, 0) #SPI bus 0, device 0
spi.max_speed_hz = 1000000 #max speed of 1MHz
value = 0

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        r = spi.xfer2([1,(8+adcnum)<<4,0])
        adcout = ((r[1]&3) << 8) + r[2]
        return adcout

while True:
    left_sensor = (readadc(7)/1024.0)*3.3
    right_sensor = (readadc(1)/1024.0)*3.3
    forward_sensor = (readadc(4)/1024)*3.3
    left_distance = 12.5/left_sensor - 0.42
    right_distance = 12.5/right_sensor - 0.42
    forward_distance = 12.5/forward_sensor - 0.42
    print('Left: '+ str(left_distance)+', Right: '+str(right_distance)+', Forward: '+str(forward_distance))
    sleep(1)
    
