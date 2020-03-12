# -*- coding: utf-8 -*-
"""
@file motors.py
This module contains classes related to the DC motors used in the ME405
lab project.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""
import pyb  # pylint: disable=import-error
import utime  # pylint: disable=import-error
import constant
import math


class Drive:
    '''This class contains all the methods necessary to drive the robot'''

    def __init__(self, M1, M2, ENC1, ENC2, MC1, MC2):
        '''This method initialized the Drive class with the motor drivers,
        encoders, and controllers specified.

        @param M1: the MotorDriver object for M1
        @param M2: the MotorDriver object for M2
        @param ENC1: the MotorDriver object for 1
        @param ENC2: the MotorDriver object for 2
        @param MC1: the motorController object for M1
        @param MC2: the motorController object for M2
        '''

        self.M1 = M1
        self.M2 = M2
        self.ENC1 = ENC1
        self.ENC2 = ENC2
        self.MC1 = MC1
        self.MC2 = MC2
        self.MC1.setKp(constant.KP)
        self.MC2.setKp(constant.KP)

        self.zero = True

    def reverseBeforeTurn(self):
        if self.setPoints(-250, -250):
            return True
        return False

    def turn(self, turnState):
        if turnState == 1:      # right turn
            degrees = -90
        if turnState == 2:
            degrees = 90        # left turn
        if turnState == 3:
            degrees = 170       # 180 turn left (compensate for loss)
        if turnState == 4:
            degrees = -90       # right turn without reverse

        point = degrees * constant.RATIO
        if self.setPoints(point, -point):
            return True
        return False

    def zeroEncoders(self):
        self.ENC1.zero()
        self.ENC2.zero()

    def read(self):
        print('enc1 ' + str(self.ENC1.read()))
        print('enc2 ' + str(self.ENC2.read()))

    def setPoints(self, point1, point2):
        if self.zero:
            print('zeroing')
            self.zeroEncoders()
            self.MC1.setPoint(point1)
            self.MC2.setPoint(point2)
            self.zero = False

        M1Pos = self.ENC1.read()
        M2Pos = self.ENC2.read()

        DC1, D1 = self.MC1.outputDutyCycle(M1Pos)
        DC2, D2 = self.MC2.outputDutyCycle(M2Pos)

        self.M1.set_duty_cycle(DC1, D1)
        self.M2.set_duty_cycle(DC2, D2)

        if self.MC1.getError() and self.MC2.getError():
            # print('MC1 ' + str(self.MC1.getError()) +
            #       ' MC2 ' + str(self.MC2.getError()))
            self.zero = True
            return True
        # else:
        #     print('MC1 err: ' + str(self.MC1.getErrorValue()))
        #     print('MC2 err: ' + str(self.MC2.getErrorValue()))
        return False

    def forward(self, level):
        self.M1.set_duty_cycle(level, 1)
        self.M2.set_duty_cycle(level, 1)
        # self.read()

    def reverse(self, level):
        self.M1.set_duty_cycle(level, -1)
        self.M2.set_duty_cycle(level, -1)

    def stop(self):
        self.M1.set_duty_cycle(0, 1)
        self.M2.set_duty_cycle(0, 1)


class MotorController:
    ''' This class controlls the motor using closed-loop proportional only control.
    '''

    def __init__(self):
        ''' This method initializes the controller with the constants needed
        for closed loop control.
        '''

        # Kp is the proportional gain for the controller and is defined
        # class Controller is called

        self.Kp = 1

        # setpoint is the desired value for the motor, in this case
        # it is the desired encoder position. Setpoint is defined
        # when class Controller is called
        self.setpoint = 0

        self.error = 0

    def getError(self):
        if abs(self.error) <= abs(0.05 * self.setpoint):
            return True
        return False

    def getErrorValue(self):
        return self.error

    def outputDutyCycle(self, position):
        ''' This method runs the control algorithm and returns an error
        reading to be used in the control system.

        # @ param position: position is the current encoder position.
        # '''

        # error is the deviation from the desired setpoint value
        self.error = self.setpoint - position

        # outputDC is the signal applied to the motor based on the error.
        # The error is multiplied by Kp and used as the PWM signal
        # sent to the motor
        outputDC = self.Kp * self.error
        direction = 1
        if outputDC < 0:
            direction = -1
            outputDC = -outputDC
        # return actuation so outputValue() can be used to control the motor
        return outputDC, direction

    def setPoint(self, point):
        ''' This method assigns the setpoint a new value for changes in set
        point during operation.
        @ param point: point desired in encoder ticks
        '''

        # setpoint is reset to the value of point
        # while running the motor controller
        self.setpoint = point

    def setKp(self, Kp):
        ''' This method assigns the proportional gain
        a new value for changes in set point during operation.
        @ param Kp: The proportional gain
        '''

        # setpoint is reset to the value of point
        # while running the motor controller
        self.Kp = Kp


class MotorDriver:
    '''This class implements a motor driver for the ME405 board.'''

    def __init__(self, directionPin, PWMpin, PWMtimer,
                 PWMchannel, freq, adjust):
        '''Creates a motor driver by initializing GPIO pins and turning the
        motor off for safety.

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

        # directionPin is the pyb.Pin object after the selcted pin has been
        # initialized and set to outputectionPin, pyb.Pin.OUT_PP)
        self.directionPin = pyb.Pin(directionPin, pyb.Pin.OUT_PP)

        # PWMpin is the specified PWM pin initialized to output
        PWMpin = pyb.Pin(PWMpin, pyb.Pin.OUT_PP)

        # tim is the pyb.Timer object associated with the PWM pin
        # set to the frequency specified
        tim = pyb.Timer(PWMtimer, freq=freq)

        # ch is the pyb.TimerChannel object associated with the specified
        # channel
        self.ch = tim.channel(PWMchannel, pyb.Timer.PWM, pin=PWMpin)

        # initialize the motor speed to 0% as a precaution
        self.ch.pulse_width_percent(0)

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

    def set_duty_cycle(self, level, direction):
        '''This method sets the duty cycle to be sent to the motor to the given
        level. Positive values cause torque in one direction, negative values
        in the opposite direction.

        @ param level: level is an unisgned integer that represents the
            duty cycle [%] to be sent to the motor
        @ param direction: direction is an integer, 1 represents forward
            and -1 represents backwards motion, False represents stop.
        '''

        if direction == 1:
            self.forward()
            self.ch.pulse_width_percent(level)
        elif direction == -1:
            self.reverse()
            self.ch.pulse_width_percent(level)
        else:
            self.forward()
            self.ch.pulse_width_percent(0)


class Encoder:
    '''This class implements reading and resetting of the motor encoder.'''

    def __init__(self, encoderPinA, chA, encoderPinB, chB,
                 timer, adjust=False):
        '''Initializes timers for the encoder.

        @param encoderPinA:
        @param chA:
        @param encoderPinB:
        @param chB:
        @param timer:
        @param adjust:
        '''

        self.adjust = adjust

        print('Setting up the encoder')

        encA = pyb.Pin(encoderPinA, mode=pyb.Pin.IN)
        encB = pyb.Pin(encoderPinB, mode=pyb.Pin.IN)

        print('Done Setting Up Encoder')

        # tim object specific to which pingroup the Encoder class is passed
        # Initialized with prescale set to zero, period set to 65535 (Hex FFFF)
        self.tim = pyb.Timer(timer, prescaler=0, period=0xFFFF)

        # Channel 1 object specific to the pingroup selected
        self.ch_1 = self.tim.channel(chA, pyb.Timer.ENC_A, pin=encA)

        # Channel 2 object specific to the pingroup selected
        self.ch_2 = self.tim.channel(chB, pyb.Timer.ENC_B, pin=encB)

        # initialize last value to 0 to start encoder at position 0.
        # Last known count of the encoder
        self.last_value = 0

        # set current position to zero as well to ensure encoder is zeroed at start
        # The current corrected position of the encoder
        self.current_position = 0

    def read(self):
        ''' This method reads the current position of the motor
        and returns it as a unsigned integer.
        @return Current position of motor 
        '''

        # read the encoder and save that value as the current value
        current_value = self.tim.counter()

        # delta is a signed value and is the difference between the current
        # reading the previous reading. If The value is positive,
        # the motor was turning clockwise, if negative,
        # it was turning counterclockwise.
        delta = current_value - self.last_value

        if delta <= -32767:
            delta = current_value + (65535 - self.last_value)

        elif delta >= 32767:
            delta = -(self.last_value + (65535 - current_value))

        else:
            pass

        self.last_value = current_value
        self.current_position += delta
        if self.adjust:
            return -self.current_position

        return self.current_position

    def zero(self):
        ''' This method resets the encoders speed to zero. 
        '''
        self.current_position = 0
