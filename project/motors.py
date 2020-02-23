# -*- coding: utf-8 -*-
"""
@file motors.py
This module contains classes related to the DC motors used in the ME405
lab project.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""
import pyb
import utime
import constant
import math

class MotorController:
    ''' This class controlls the motor speed using closed-loop
        proportional (Kp) control.'''
    
    def __init__ (self, Kp, desiredSpeed):
        ''' This method initializes the controller with
        the constants needed for closed loop control.
        @ param Kp: Kp is the proportional gain for the controller.
        @ param desiredSpeed: desiredSpeed is the desired value
            that the motor is trying to reach. [ft/s]'''
        
        ## Kp is the proportional gain for the controller
        # Kp is in units of % Duty Cycle per ft/s
        self.Kp = Kp

        ## desiredSpeed is the desired speed for the motor
        self.desiredSpeed = desiredSpeed

        ## lastDC is the last Duty Cycle sent to the motor.
        # Initialized to 0.
        self.lastDC = 0
        
    def outputDC (self, currentSpeed):
        ''' This method runs the control algorithm and
        returns a corrected duty cycle to the motor via PWM
        @ param currentSpeed: currentSpeed is the current speed
            measured by the encoder. [ticks/ms]'''

        ## currentSpeed needs to be converted from [ticks/ms] to [ft/s]
        currentSpeed = currentSpeed * 1000 * (1/900) * 2 * math.pi * (constant.WHEEL_RADIUS/12)
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
            in main that the controller is tyring reach.'''
        
        ## desiredSpeed is reset to the input value while running the motor controller
        self.desiredSpeed = desiredSpeed

    def setKp (self, Kp):
        ''' This method assigns the proportional control gain
        a new value for special cases during operation.
        i.e. during motor startup to overcome stiction.
        @ param Kp: Kp is the updated value input during
            operation that replaces the intial value of Kp.'''      

        ## Kp is reset to the value of Kp while running the motor controller
        self.Kp = Kp

class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board. '''
    def __init__ (self, directionPin, PWMpin, PWMtimer, PWMchannel, freq):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. 
        @param directionPin: directionPin is a pyb.Pin.board object
            for the motor direction output pin (high is forwards, low is backwards)
        @param PWMpin: PWMpin is a pyb.Pin.board object for the motor 
            PWM control output pin
        @param PWMtimer: PWMtimer is the PWM timer associated with the pin
        @param PWMchannel: PWMchannel is the PWM channel associated with the timer
        @param freq: freq is the frequency in Hz at which to run the PWM'''
        
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
        
    def set_duty_cycle (self, level, direction):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @ param level: level is an unisgned integer that represents the 
        duty cycle [%] to be sent to the motor
        @ param direction: direction is a boolean, true represents forward
        and false represents backwards motion'''
        
        if direction == True:
            self.ch.pulse_width_perself.directionPin.high()
            self.ch.pulse_width_percent (level)
        else:
            self.ch.pulse_width_perself.directionPin.low()
            self.ch.pulse_width_percent (level)
