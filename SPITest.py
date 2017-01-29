import spidev
from time import sleep
import sys

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
    value = readadc(0)
    print('Value: '+ str(value))
    sleep(1)
    
