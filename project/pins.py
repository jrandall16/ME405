# -*- coding: utf-8 -*-
"""
@file pins.py
This module contains all the pin objects that will be used by the bots in an
easy to read format to use.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""

import pyb  # pylint: disable=import-error


def output(pin):
    """This function sets the desired pin to an output pin.

    @param pin: pin is a pyb.Pin.board object of the pin to be set
        as an output.
    """
    return pyb.Pin(pin, pyb.Pin.OUT_PP)


def input(pin):
    """This function sets the desired pin to an input pin.

    @param pin: pin is a pyb.Pin.board object of the pin to be set
        as an input.
    """
    return pyb.Pin(pin, pyb.Pin.IN)


# ENC1A
ENC1A = pyb.Pin.board.PB6

# ENC1B
ENC1B = pyb.Pin.board.PB7

# ENC2A
ENC2A = pyb.Pin.board.PC6

# ENC2B
ENC2B = pyb.Pin.board.PC7

# MOTOR1 PWM
M1PWM = pyb.Pin.board.PA7

# MOTOR2 PWM
M2PWM = pyb.Pin.board.PA6

# MOTOR1 Direction
M1DIR = pyb.Pin.board.PA8

# MOTOR2 Direction
M2DIR = pyb.Pin.board.PA9

# IR input
IR = pyb.Pin.board.PA15

# SDA
SDA = pyb.Pin.board.PB9

# SCL
SCL = pyb.Pin.board.PB8


# Ultrasonic Distance sensor 4 echo - left facing
US_DIST_ECHO_4 = pyb.Pin.board.PB1  # set in pinout, can change if needed

# Ultrasonic Distance sensor 3 echo - right facing
US_DIST_ECHO_3 = pyb.Pin.board.PC8  # set in pinout, can change if needed

# Ultrasonic Distance sensor 2 echo - forward facing
US_DIST_ECHO_2 = pyb.Pin.board.PB2  # changed4


# Ultrasonic Distance sensor 1 echo - rear facing
US_DIST_ECHO_1 = pyb.Pin.board.PB14  # set in pinout, can change if needed

# Ultrasonic Distance sensor trigger
US_DIST_TRIG = pyb.Pin.board.PB13  # set in pinout, can change if needed

# IR Reflectance Sensors
QRT_EN = pyb.Pin.board.PC1

QRT1 = pyb.Pin.board.PB4
QRT2 = pyb.Pin.board.PA4
QRT3 = pyb.Pin.board.PA0
QRT4 = pyb.Pin.board.PA5
QRT5 = pyb.Pin.board.PB0
QRT6 = pyb.Pin.board.PB5

QRT_ARRAY = [QRT1, QRT2, QRT3, QRT4, QRT5, QRT6]
