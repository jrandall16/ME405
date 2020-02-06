# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 09:14:00 2020

@author: melab15
"""

'''@file main.py'''
import encoder as enc
import motor_driver
import utime
import controller
motor = motor_driver.MotorDriver()
motor.set_duty_cycle(30)
encB = enc.Encoder('B')

ctr = controller.Controller('0.001')
# output_level = ctr.setOutput(encB.read())
# motor.set_duty_cycle(output_level)
try:
    while True:
        print (encB.read() + ',' + utime.ticks_ms())
        utime.sleep_ms(10)

except KeyboardInterrupt:
    motor.set_duty_cycle(0)
    
    


    
    
    

