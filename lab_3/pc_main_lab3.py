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
motor1_data = []
motor2_data = []
time_ms1 = []
position1 = []
time_ms2 = []
position2 = []

## define an amount of time to run the motor and collect step response data ( set to 6 for our test case )
t_end = time.time() + 3

# initiate a try block to open and read data from the serial port
try:
    # write a Crtl+D to soft reboot the board
    serial_port.write('\x04')

    # give the board 1 second to boot up
    time.sleep(1)
    
    # while the time is less than t_end, read the data from the serial_port
    while time.time() < t_end:

        x = serial_port.read()
        # print(x.decode())
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

        newdata.append(point.split(',',3))
    
    for point in newdata:
        if point[0] == str(1):
            motor1_data.append([int(point[1]), int(point[2])])
        elif point[0] == str(2):
            motor2_data.append([int(point[1]), int(point[2])])
        else:
            pass
    print (motor1_data)
    print (motor2_data)

    ticks_corrected1 = int(motor1_data[0][1])
    ticks_corrected2 = int(motor2_data[0][1])
    for point in motor1_data:
        position1.append(point[0])
        time_ms1.append(point[1] - ticks_corrected1)

    for point in motor2_data:
        position2.append(point[0])
        time_ms2.append(point[1] - ticks_corrected2)

    pyplot.plot(time_ms1, position1, 'g-', time_ms2, position2, 'b--')
    pyplot.title('Position vs Time')
    pyplot.show ()

# close the serial port when keyboard interupt is thrown
except KeyboardInterrupt:
    serial_port.write('\x03')
    serial_port.close()
