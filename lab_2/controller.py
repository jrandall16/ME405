# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import pyb
#import encoder
#import motor_driver

class Controller:
    ''' This class controlls the motor using proportional only control
    '''
    
    def __init__ (self, position):
        ''' This method initializes the controller.
        @ param Kp:
        @ param setpoint:
        @ param gain:
        '''
        self.Kp = 0.25
        self.setpoint = 4
        self.gain = 10
        self.position = position
        
    def controlla (self):
        ''' This method runs the control algorithm and returns an error reading 
        to be used in the control system.
        '''
        
        error = self.setpoint - self.position
        actuation = self.Kp*error
        return actuation
        
    def setPoint (self):
        ''' This method assigns the setpoint a new value for changes in set point
        during operation.
        '''
    def setGain (self):
        ''' This method assigns the control gain(s) a new value for special cases
        during operation. i.e. during motor startup to overcome stiction.
        '''      
        