"""
Created on Thu Jan  9 09:14:00 2020

@author: Jacob Randall and Connor Bush
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
t_end = time.time() + 4

# initiate a try block to open and read data from the serial port
try:
    # write a Crtl+D to soft reboot the board
    serial_port.write('\x04')

    # give the board 1 second to boot up
    time.sleep(1)
    
    # while the time is less than t_end, read the data from the serial_port
    while time.time() < t_end:

        x = serial_port.read()

        # edit the data to remove unwanted return characters (\r and \n)
        data.append(x.decode().rstrip())

    # give the board 0.5 seconds to finish reading any data    
    time.sleep(0.5)

    # write a Ctrl+C to interrupt the board
    serial_port.write('\x03')

    # close the serial_port
    serial_port.close()
    
    # for each data read, split the values into a column of position and time
    for point in data:

        newdata.append(point.split(',',2))
    
    # find the index of string 'firstline' to identify the beginning of position and time data
    firstline = ['firstline']

    firstline = newdata.index(firstline)

    # define the initial time read
    ticks_corrected = int(newdata[firstline + 1][1])
    
    # append position and time data to the corresponding list
    for point in newdata:
        
        # if the index of the data is greater than the index of firstline, store the data
        if newdata.index(point) > firstline:
            
            # position data
            position.append(int(point[0]))

            # time data
            time_ms.append(int(point[1]) - ticks_corrected)

        else:
            pass

    # plot the data: a function of position versus time
    pyplot.plot(time_ms, position)
    pyplot.title('Position vs Time')
    pyplot.show ()

# close the serial port when keyboard interupt is thrown
except KeyboardInterrupt:
    serial_port.write('\x03')
    serial_port.close()


    

