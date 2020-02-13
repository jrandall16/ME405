""" @file main.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and some queues. 

    @author JR Ridgely

    @copyright (c) 2015-2020 by JR Ridgely and released under the Lesser GNU
        Public License, Version 3. 
"""

import pyb
from micropython import const, alloc_emergency_exception_buf
import gc

import cotask
import task_share
import print_task
import busy_task
import controller
import encoder as enc
import motor_driver
import utime

# Allocate memory so that exceptions raised in interrupt service routines cangenerate useful diagnostic printouts
alloc_emergency_exception_buf (100)

## Define a method to run motor 1
def motor_1 ():
    ''' Define a task to run both motors in order. Configure the motor using the motor_driver.py file. Print the data to the serial port and plot the data in pc_main_lab3'''

    # call class MotorDriver()
    motor = motor_driver.MotorDriver('A10', 20000)

    # call class Controller()
    ctr = controller.Controller(0.01, 16000, 30)
    
    ## define the encoder that is used to read the motor position
    encB = enc.Encoder('B')
    
    # run the proportional contorller on the motor and feed the data into the shares and queues using put()
    x = True
    while True:

        # set the motor duty cycle using class Controller()
        motor.set_duty_cycle(ctr.outputValue(encB.read()))

        # create a string of data to be plotted
        data = '1, ' + str(encB.read()) + ', ' + str(utime.ticks_ms()) + '\r\n'

        # print data every other pass through the while loop
        if x == True:
            print_task.put (data)

        # yield to another task and resume at this line
        yield (0)

## Define a method to run motor 2
def motor_2 ():
    ''' Define a task to run both motors in order. Configure the motor using the motor_driver.py file. Print the data to the serial port and plot the data in pc_main_lab3'''

    # call class MotorDriver()
    motor_2 = motor_driver.MotorDriver('C1', 20000)

    # call class Controller()
    ctr_2 = controller.Controller(0.01, 16000, 30)

    ## define the encoder that is used to read the motor position
    encC = enc.Encoder('C')

    # define x to be True to collect half of the data points an allow more time for printing data
    x = True

    while True:
        # initialize the motor controller using class Controller()
        motor_2.set_duty_cycle(ctr_2.outputValue(encC.read()))

        # create a string of data to be plotted
        data = '2, ' + str(encC.read()) + ', ' + str(utime.ticks_ms()) + '\r\n'

        # print data every other pass through the while loop
        if x == True:
            print_task.put (data)
        x = not x

        # yield to another task and resume at this line
        yield (0)

# # ============================================================================= # #

if __name__ == "__main__":

    try:
        print ('\033[2JTesting scheduler in cotask.py\n')

        # Intitialize the tasks for each motor controller using Task()
        m1 = cotask.Task (motor_1, name = 'Motor 1', priority = 1, period = 40, profile = True, trace = False)
        m2 = cotask.Task (motor_2, name = 'Motor 2', priority = 1, period = 40, profile = True, trace = False)

        # add each task to the task list                     
        cotask.task_list.append (m1)
        cotask.task_list.append (m2)

        # execute the task list using the priority attribute of each task
        while True:
            cotask.task_list.pri_sched ()

        # Run the memory garbage collector to ensure memory is as defragmented as possible before the real-time scheduler is started
        gc.collect ()

    # If a keyboard interrupt is thrown, set the motor duty cycles to 0
    except KeyboardInterrupt:
        motor = motor_driver.MotorDriver('A10', 20000)
        motor.set_duty_cycle(0)

        motor_2 = motor_driver.MotorDriver('C1', 20000)
        motor_2.set_duty_cycle(0)