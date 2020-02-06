# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 09:14:00 2020

@author: melab15
"""

'''@file motor_randall_bush.py'''
import pyb


class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board. '''
    def __init__ (self):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. '''
        print ('Creating a motor driver')
        pinA10 = pyb.Pin (pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
        pinA10.high()
        pinPB4 = pyb.Pin (pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
        pinPB5 = pyb.Pin (pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
        tim3 = pyb.Timer (3, freq=20000)
        
        ## Channel 2 controls pin B5 of the Nucleo board
        self.ch2 = tim3.channel (2, pyb.Timer.PWM, pin=pinPB5)
        
        ## Channel 1 controls pin B4 of the Nucleo board
        self.ch1 = tim3.channel (1, pyb.Timer.PWM, pin=pinPB4)
        
        self.ch2.pulse_width_percent (0)
        self.ch1.pulse_width_percent (0)
        
        return
        
    def set_duty_cycle (self, level):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
        cycle of the voltage sent to the motor '''
        #print ('Setting duty cycle to ' + str (level))
        
        if level < 0:
            self.ch1.pulse_width_percent (0)
            self.ch2.pulse_width_percent (abs(level))
        else:
            self.ch2.pulse_width_percent (0)
            self.ch1.pulse_width_percent (abs(level))
            
        return level

    
