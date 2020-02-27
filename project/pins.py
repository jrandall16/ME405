# -*- coding: utf-8 -*-
"""
@file pins.py
This module contains all the pin objects that will be used by the bots in an
easy to read format to use.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""

import pyb # pylint: disable=import-error

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
IR = pyb.Pin.board.PA5

# SDA
SDA = pyb.Pin.board.PB9

# SCL
SCL = pyb.Pin.board.PB8

# Distance sensor enable
DIST_EN = pyb.Pin.board.PC8

# Distance sensor trigger
DIST = pyb.Pin.board.PA9

# Ultrasonic Distance sensor enable
US_DIST_EN = pyb.Pin.board.PC6

# Ultrasonic Distance sensor trigger
US_DIST = pyb.Pin.board.PA10

# IR Reflectance Sensors
QRT1 = pyb.Pin.board.PB5
QRT2 = pyb.Pin.board.PC2
QRT3 = pyb.Pin.board.PB15
QRT4 = pyb.Pin.board.PA0
QRT5 = pyb.Pin.board.PC3
QRT6 = pyb.Pin.board.PA15

