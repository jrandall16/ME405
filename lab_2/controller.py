# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import utime

class Controller:
    ''' This class controlls the motor using proportional only control
    '''
    
    def __init__ (self, Kp, setpoint, gain):
        ''' This method initializes the controller.
        @ param Kp: Kp is the proportional gain for the controller
        @ param setpoint: setpoint is the desired value that eh motor is trying to reach
        @ param gain: gain is the motors steady state gain determined experimentally from step response data
        '''
        
        ## Kp is the proportional gain for the controller and is defined when class Controller is called
        self.Kp = Kp

        ## setpoint is the desired value for the motor, in this case it is the desired encoder position. It is defined when class Controller is called
        self.setpoint = setpoint

        ## gain is the motor steady state gain and is defined when class Controller is called
        self.gain = gain
        
    def outputValue (self, position):
        ''' This method runs the control algorithm and returns an error reading 
        to be used in the control system.
        '''

        ## error is the deviation from the desired setpoint value
        error = self.setpoint - position

        ## actuation is the signal appleid to the motor based on the error. The error is multiplied by Kp and used as the PWM signal sent to the motor
        actuation = self.Kp*error

        # return actuation so outputValue() can be used to control the motor
        return actuation
        
    def setPoint (self, point):
        ''' This method assigns the setpoint a new value for changes in set point
        during operation.
        '''
        
        ## setpoint is reset to the value of point while running the motor controller
        self.setpoint = point


    def setGain (self, gain):
        ''' This method assigns the control gain(s) a new value for special cases
        during operation. i.e. during motor startup to overcome stiction.
        '''      
        ## Kp is reset to the value of gain while running the motor controller
        self.Kp = gain

    # def readData(self, position):
    #     ''' This method reads the data from the serial port and organizes it into columns of time and motor position.
    #     '''

    #     self.data = (utime.ticks_ms(), ',', position, '\n')

