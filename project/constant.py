# -*- coding: utf-8 -*-
"""
@file constant.py
This module contains all the constants used throughout the code so they
can be modified easily in one place. Constant names are self explained

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""
START = 12

WHEEL_RADIUS = 0.75     # [in]
KP = 1     # [analyze units]
RATIO = 4.75       # ticks per degree (5.83 but had to adjust)

MOT_FREQ = 16000
MOT_PWM_TIMER = 3
MOT1_PWM_CH = 2
MOT2_PWM_CH = 1

ENC1_TIMER = 4
ENC1A_CH = 1
ENC1B_CH = 2

ENC2_TIMER = 8
ENC2A_CH = 1
ENC2B_CH = 2

IR_TIMER = 2
IR_CH = 1
