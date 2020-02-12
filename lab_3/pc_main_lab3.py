"""
Created on Wed Feb 05 09:14:00 2020

@author: Jacob Randall and Connor Bush

Collect position and time data from the motor controller through a serial port. Clean up the data and plot position versus time to find the steady state motor gain and time constant. 
"""

from matplotlib import pyplot
import serial_controller
import time

## initialize the serial_port as the port defined by the pc
serial_port = serial_controller.Serial('/dev/cu.usbmodem205537A735412')

# initialize blank arrays to be filled with data
data = []
newdata = []
time_ms = []
position = []

## define an amount of time to run the motor and collect step response data ( set to 6 for our test case )
t_end = time.time() + 2

# initiate a try block to open and read data from the serial port
try:
    # write a Crtl+D to soft reboot the board
    serial_port.write('\x04')

    # give the board 1 second to boot up
    time.sleep(1)
    
    # while the time is less than t_end, read the data from the serial_port
    while time.time() < t_end:

        x = serial_port.read()

        print(x.decode())

    # give the board 0.5 seconds to finish reading any data    
    time.sleep(0.5)

    # write a Ctrl+C to interrupt the board
    serial_port.write('\x03')

    # close the serial_port
    serial_port.close()

# close the serial port when keyboard interupt is thrown
except KeyboardInterrupt:
    serial_port.write('\x03')
    serial_port.close()
