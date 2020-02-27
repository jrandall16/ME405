# -*- coding: utf-8 -*-
"""
@file motors.py
This module contains classes related to the DC motors used in the ME405
lab project.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""
import pyb # pylint: disable=import-error
import utime # pylint: disable=import-error
import constant
import math

class MotorController:
    ''' This class controls the motor speed using closed-loop
        proportional (Kp) control.
    '''
    
    def __init__ (self, Kp):
        ''' This method initializes the controller with
        the constants needed for closed loop control.
        @ param Kp: Kp is the proportional gain for the controller.
        @ param desiredSpeed: desiredSpeed is the desired value
            that the motor is trying to reach. [ft/s]
        '''
        
        ## Kp is the proportional gain for the controller
        # Kp is in units of % Duty Cycle per ft/s
        self.Kp = Kp

        ## desiredSpeed is the desired speed for the motor
        # Initialized to 0.
        self.desiredSpeed = 0

        ## lastDC is the last Duty Cycle sent to the motor.
        # Initialized to 0.
        self.lastDC = 0
        
    def outputDC (self, currentSpeed):
        ''' This method runs the control algorithm and
        returns a corrected duty cycle to the motor via PWM
        @ param currentSpeed: currentSpeed is the current speed
            measured by the encoder. [ticks/ms]
        '''

        ## currentSpeed needs to be converted from [ticks/ms] to [ft/s]
        currentSpeed = currentSpeed * 1000 * (1/900) * 2 * \
                        math.pi * (constant.WHEEL_RADIUS/12)
        ## error is the deviation from the desired speed value [ft/s]
        error = self.desiredSpeed - currentSpeed

        ## outputDC is the new Duty Cycle to be sent to the motor
        outputDC = self.lastDC + (self.Kp * error)
        
        self.lastDC = outputDC

        # return the outputDC 
        return outputDC
        
    def setDesiredSpeed (self, desiredSpeed):
        ''' This method assigns the desiredSpeed a new
        value for changes in desired Speed during operation.
        @ param point: speed is the encoder location defined
            in main that the controller is tyring reach.
        '''
        
        ## desiredSpeed is reset to the input value while
        # running the motor controller
        self.desiredSpeed = desiredSpeed

    def setKp (self, Kp):
        ''' This method assigns the proportional control gain
        a new value for special cases during operation.
        i.e. during motor startup to overcome stiction.
        @ param Kp: Kp is the updated value input during
            operation that replaces the intial value of Kp.
        '''      

        ## Kp is reset to the value of Kp while running the motor controller
        self.Kp = Kp

class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board.
    '''
    def __init__ (self, directionPin, PWMpin, PWMtimer, PWMchannel, freq, adjust):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. 
        @param directionPin: directionPin is a pyb.Pin.board object
            for the motor direction output pin
            (high is forwards, low is backwards)
        @param PWMpin: PWMpin is a pyb.Pin.board object for the motor 
            PWM control output pin
        @param PWMtimer: PWMtimer is the PWM timer associated with the pin
        @param PWMchannel: PWMchannel is the PWM channel
            associated with the timer
        @param freq: freq is the frequency in Hz at which to run the PWM
        @param adjust: adjust is a boolean, True means flip the direction of 
            rotation
        '''
        
        ## directionPin is the pyb.Pin object after the selcted pin has been 
        # initialized and set to output
        self.directionPin = pyb.Pin (directionPin, pyb.Pin.OUT_PP)
        
        # PWMpin is the specified PWM pin initialized to output
        PWMpin = pyb.Pin (PWMpin, pyb.Pin.OUT_PP)

        # tim is the pyb.Timer object associated with the PWM pin
        # set to the frequency specified
        tim = pyb.Timer (PWMtimer, freq=freq)

        ## ch is the pyb.TimerChannel object associated with the specified
        # channel
        self.ch = tim.channel (PWMchannel, pyb.Timer.PWM, pin=PWMpin)

        # initialize the motor speed to 0% as a precaution
        self.ch.pulse_width_percent (0)

        # initialize adjust variable to the class scope
        self.adjust = adjust
        # initialize direction to forward
        self.forward()
    
    def forward(self):
        if self.adjust:
            self.directionPin.high()
        else:
            self.directionPin.low()

    def reverse(self):
        if self.adjust:
            self.directionPin.low()
        else:
            self.directionPin.high()
        
    def set_duty_cycle (self, level, direction):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @ param level: level is an unisgned integer that represents the 
            duty cycle [%] to be sent to the motor
        @ param direction: direction is an integer, 1 represents forward
            and -1 represents backwards motion, False represents stop.
        '''
        
        if direction == 1:
            self.forward()
            self.ch.pulse_width_percent (level)
        elif direction == -1:
            self.reverse()
            self.ch.pulse_width_percent (level)
        else:
            self.forward()
            self.ch.pulse_width_percent (0)
    
    def turn (self, amount):
        ''' This method turns the bot in increments of 90 degrees by setting
        the pulse_width_percent for a duration of time according to how far
        of a turn is requested'''

        if amount == 1:
            self.set_duty_cycle('amount',1)
        elif amount == 2:
            self.set_duty_cycle('amount',1)
        elif amount == 3:
            self.set_duty_cycle('amount',1)
        elif amount == 4:
            self.set_duty_cycle('amount',1)
        elif amount == -1:
            self.set_duty_cycle('amount',2)
        elif amount == -2:
            self.set_duty_cycle('amount',2)
        elif amount == -3:
            self.set_duty_cycle('amount',2)
        elif amount == -4:
            self.set_duty_cycle('amount',2)

class Encoder:
    ''' This class implements reading and resetting of the motor encoder
    '''
    def __init__ (self, encoderpinA, channelA, encoderpinB, channelB, timer):
        ''' Initializes timers for the encoder.
        @param pingroup Input of a character 'B' or 'C' representing 
        pingroups B6/B7 or C6/C7 on the cpu respectively
        '''
        
        print ('Setting up the encoder')

        encA = pyb.Pin (encoderpinA, mode = pyb.Pin.IN)
        encB = pyb.Pin (encoderpinB, mode = pyb.Pin.IN)

        print ('Done Setting Up Encoder')

        ## tim object specific to which pingroup the Encoder class is passed
        # Initialized with prescale set to zero, period set to 65535 (Hex FFFF)
        self.tim = pyb.Timer (timer, prescaler=0, period=0xFFFF)

        ## Channel 1 object specific to the pingroup selected
        self.ch_1 = self.tim.channel(channelA, pyb.Timer.ENC_A, pin = encA)

        ## Channel 2 object specific to the pingroup selected
        self.ch_2 = self.tim.channel(channelB, pyb.Timer.ENC_B, pin = encB)
        
        # initialize last value to 0 to start encoder at position 0
        ## Last known count of the encoder
        self.last_value = 0

        ## The current corrected position of the encoder
        self.current_value = 0

        ## The current speed of the encoder 
        self.currentSpeed = 0

        # initialize last value to 0 to start timer at 0
        ## The last time read by the timer
        self.last_time = 0

        # set current time to zero as well to ensure timer is zeroed at start
        ## The current time read by the timer
        self.current_time = 0
        
    def read (self):
        ''' This method reads the current position of the motor
        and returns it as a unsigned integer.
        @return Current position of motor 
        '''
        # read the encoder and save that value as the current value
        current_value = self.tim.counter()
        current_time = utime.ticks_ms()
        

        # delta is a signed value and is the difference between the current
        # reading the previous reading. If The value is positive,
        # the motor was turning clockwise, if negative, it was turning
        # counterclockwise.
        delta = (current_value - self.last_value)

        if delta <= -32767:
            delta = current_value + (65535 - self.last_value)

        elif delta >= 32767:
            delta = -(self.last_value + (65535 - current_value))

        else:
            pass
        
        # using the adjusted position data, find the speed of the motor
        # in ticks per millisecond
        tickspertime = (current_value - self.last_value) \
                        / (current_time - self.last_time)

        # set the current value of time and position to the last value, so the
        # next time through a new change is computed
        self.last_value = current_value
        self.last_time = current_time
        self.currentSpeed += tickspertime
        return self.currentSpeed

    def zero (self):
        ''' This method resets the encoders speed to zero. 
        '''    
        self.currentSpeed = 0