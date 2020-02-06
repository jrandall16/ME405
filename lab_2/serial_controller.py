"""
Created on Wed Feb 05 09:14:00 2020

@author: Jacob Randall and Connor Bush

Open, read and write a generic serial port. Use in combinatino with pc_main to collect and plot the data passed through the serial port. 
"""

import time
import serial


class Serial:
    ''' This class initializes the serial port used by the Nucleo board, reads data from the port as a string, writes the data to a PuTTy terminal and closes the serial port.
    '''

    def __init__(self, port):
        '''Opens a serial port communication between the Nucleo board and PuTTy terminal.
        @ param port: port is the serial port in use. The port is defined the port in pc_main.py.
        '''

        print('Opening serial port')

        ## initialize a serial port with baudrate for Nucleo board and timeout value of 1 second so readlines() does not get stuck in an endless reading state
        self.ser = serial.Serial(port, baudrate = 115200, timeout = 1)

        # verify the port information
        print('Serial port opened at: ' + port)

    def read(self):
        ''' This method reads the serial data if the port is open.
        '''

        # reads one line of the data from the serial port if the port is open
        if self.ser.is_open == True:

            # read the line of data from the serial port
            data = self.ser.readline()
            return data

        else:
            # return an error message here
            return None

    def write(self, data):
        ''' This method writes a string input to the serial port from the data collected.
        @ param data: data is a string of data that is written to the port.
        '''

        # writes the string of data to the serial port if the port is open
        if self.ser.is_open == True:

            # encode the data so it is not in binary
            self.ser.write(data.encode())

        else:
            # return an error message here
            pass

    def close(self):
        ''' This method closes the serial port and verifies that it is closed by printing a statement.
        '''

        # close the serial port
        self.ser.close()

        # verify the port is closed
        print ('Serial Port is Closed')