# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import utime

class Controller:
    ''' This class controlls the motor using proportional only control
    '''
    
    def __init__ (self, position):
        ''' This method initializes the controller.
        @ param Kp: Kp is the proportional gain for the controller
        @ param setpoint: setpoint is the desired value that eh motor is trying to reach
        @ param gain: gain is the motors steady state gain determined experimentally from step response data
        '''
        
        ## Kp is the proportional gain for the controller
        self.Kp = 0.001

        ## setpoint is the desired value for the motor, in this case it is the desired encoder position
        self.setpoint = 16000

        ## gain is the motor steady state gain
        self.gain = 10

        ## position is the current value for the motor, in this case it is the current encoder position
        self.position = position
        
    def controlla (self):
        ''' This method runs the control algorithm and returns an error reading 
        to be used in the control system.
        '''

        ## errror is the deviation from the desired value
        error = self.setpoint - self.position

        ## actuate is the signal appleid to the motor based on the error. The error is multiplied by Kp and used as the PWM signal sent to the motor
        actuation = self.Kp*error

        return actuation
        
    def setPoint (self):
        ''' This method assigns the setpoint a new value for changes in set point
        during operation.
        '''
        
        ## setpoint is reset to the value of point while running the motor controller
        self.setpoint = point


    def setGain (self):
        ''' This method assigns the control gain(s) a new value for special cases
        during operation. i.e. during motor startup to overcome stiction.
        '''      
        ## Kp is reset to the value of gain while running the motor controller
        self.Kp = gain

    def readData(self, position):
        ''' This method reads the data from the serial port and organizes it into columns of time and motor position.
        '''

        self.data = (utime.ticks_ms(), ',', position, '\n')

