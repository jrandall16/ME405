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

# call class MotorDriver()
motor = motor_driver.MotorDriver()

# call class Controller()
ctr = controller.Controller()

# define the encoder that is used to read the motor position
encB = enc.Encoder('B')

# initiate a try block with exception for emergency stop by keyboard interupt
try:
    print ('firstline')
    while True:
        #set the duty cycle to the output of controller function outputValue() using the current position of the encoder to determine the actuation signal
        motor.set_duty_cycle(ctr.outputValue(encB.read()))

        # print the data into the terminal to be read by the pc
        print (str(encB.read()) + ',' + str(utime.ticks_ms()))

        # print data every 10 milliseconds
        utime.sleep_ms(10)



# set duty cycle of the motor to 0 if a keyboard interput is thrown
except KeyboardInterrupt:
    motor.set_duty_cycle(0)
    
    


    
    
    

