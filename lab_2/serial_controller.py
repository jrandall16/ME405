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
        '''Opens a serial port to communicate with the nucleo board
        ...
        '''
        print('Opening serial port')
        self.ser = serial.Serial(port, baudrate = 115200, timeout = 1)
        print('Serial port opened at: ' + port)

    def read(self):
        if self.ser.is_open == True:
            data = self.ser.readline()
            return data
        else:
            # return an error message here
            return None

    def write(self, data):
        if self.ser.is_open == True:
            self.ser.write(data.encode())
        else:
            # throw error
            pass

    def close(self):
        self.ser.close()
        print ('Serial Port is Closed')

# enc1 = enc.Encoder('B')
# enc2 = enc.Encoder('C')

# data1 = []
# data2 = []

# if ser.is_open == True:
#     command = ser.read()
    
#     if command == 'ye':
#         time.sleep(.1)
#         data1 = enc1.read()
#         data2 = enc2.read()
#         ser.write(data1)
#         ser.write(data2)
        
    
    
# ser.close()