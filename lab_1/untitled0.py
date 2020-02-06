# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 08:39:08 2020

@author: melab15
"""

'''@file motor_randall_bush.py'''
import pyb


class EncoderReading:
        ''' This class reads the encoder on the motor. The motor channels are
        connected to pins B6 and B7 on the Shoe of Brian'''
        def __init__(self):
            ''' This definition initializes the encoder reading'''
            self.PinB6 = pyb.Pin (pyb.Pin.board.B6, pyb.Pin.IN)
            self.PinB7 = pyb.Pin (pyb.Pin.board.B7, pyb.Pin.IN)
            timer = pyb.Timer(4, prescaler=0, period= 0xFFFF)
            self.channe= timer.channel(1, pyb.Timer.ENC_AB, pin = PinB6)
            
        