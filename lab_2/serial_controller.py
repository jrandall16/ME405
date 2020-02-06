# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 09:14:00 2020

@author: melab15
"""

'''@file main.py'''
# import encoder as enc
import time
import serial


class Serial:
    '''define here
    '''

    def __init__(self, port):
        '''Opens a serial port communication between the Nucleo board and PuTTy terminal
        @ param port: port is the serial port which is in use. define the port in pc_main
        '''

        print('Opening serial port')

        ## initialize a serial port with baudrate for Nucleo board and timeout value of 1 second so readlines() does not get stuck in an infinite reading state
        self.ser = serial.Serial(port, baudrate = 115200, timeout = 1)

        # verify the port information
        print('Serial port opened at: ' + port)

    def read(self):
        ''' This method reads the serial data if the port is open
        '''
        # reads on line of the data from the serial port if the port is open
        if self.ser.is_open == True:
            data = self.ser.readline()
            return data
        else:
            # return an error message here
            return None

    def write(self, data):
        ''' This method writes a string input to the serial port from the data collected
        @ param data: data is a string of datat that is written to the port
        '''

        # writes the string of data to the serial port if the port is open
        if self.ser.is_open == True:
            self.ser.write(data.encode())
        else:
            # return an error message here
            pass

    def close(self):
        ''' This method closes the serial port and verifies that it is closed by printing a statement
        '''
        self.ser.close()
        print ('Serial Port is Closed')