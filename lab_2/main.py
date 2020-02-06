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
# motor.set_duty_cycle(30)
encB = enc.Encoder('B')

ctr = controller.Controller(encB.read())
# output_level = ctr.setOutput(encB.read())
# motor.set_duty_cycle(output_level)
try:
    print ('firstline')
    while True:
        motor.set_duty_cycle(ctr.outputValue())
        print (str(encB.read()) + ',' + str(utime.ticks_ms()))
        utime.sleep_ms(10)

except KeyboardInterrupt:
    motor.set_duty_cycle(0)
    
    


    
    
    

