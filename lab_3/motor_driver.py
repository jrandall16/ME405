"""
Created on Wed Feb 05 09:14:00 2020

@author: Jacob Randall and Connor Bush

Send the motor a pulse width modulation (PWM) signal to define the duty cycle of the motor. 
"""

import pyb


class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board. '''
    def __init__ (self, pingroup, freq):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. 
        @param pingroup
        '''
        print ('Creating a motor driver')

        if pingroup == 'A10':

            pin1 = pyb.Pin (pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
            pin1.high()
            pin2 = pyb.Pin (pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
            pin3 = pyb.Pin (pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
            tim = pyb.Timer (3, freq=freq)
        elif pingroup == 'C1':
            pin1 = pyb.Pin (pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
            pin1.high()
            pin2 = pyb.Pin (pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
            pin3 = pyb.Pin (pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
            tim = pyb.Timer (5, freq=freq)
        
        ## Channel 2 controls pin B5 of the Nucleo board
        self.ch2 = tim.channel (2, pyb.Timer.PWM, pin=pin3)
        
        ## Channel 1 controls pin B4 of the Nucleo board
        self.ch1 = tim.channel (1, pyb.Timer.PWM, pin=pin2)
        
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

    
