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

# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
alloc_emergency_exception_buf (100)

## Define a method to run motor 1
def motor_1 ():
    ''' Define a task to run both motors in order. Configure the motor using the motor_driver.py file. Store the data collected from each in a
    queue and extract this data for plotting later'''

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
        data = '1, ' + str(encB.read()) + ', ' + str(utime.ticks_ms()) + '\r\n'
        if x == True:
            print_task.put (data)
        x = not x
        # if the queue is not full, fill values for the queue and the share
        # if q0.full() == False:
        #     q0.put (encB.read())
        #     q0.put (utime.ticks_ms())

        # s0p.put(encB.read())
        # s0t.put (utime.ticks_ms())
        yield (0)

## Define a method to run motor 2
def motor_2 ():
    ''' Define a task to run the first motor. Configure the motor using the motor_driver.py file.'''
    motor_2 = motor_driver.MotorDriver('C1', 20000)

    # call class Controller()
    ctr_2 = controller.Controller(0.01, 16000, 30)

    ## define the encoder that is used to read the motor position
    encC = enc.Encoder('C')
    x = True
    while True:
        motor_2.set_duty_cycle(ctr_2.outputValue(encC.read()))
        data = '2, ' + str(encC.read()) + ', ' + str(utime.ticks_ms()) + '\r\n'
        if x == True:
            print_task.put (data)
        x = not x
        yield (0)
# # =============================================================================
# run main continuously
if __name__ == "__main__":
    try:
        print ('\033[2JTesting scheduler in cotask.py\n')

        # Establish a set of shares and queues for both to test if either is working
        # Set up shares for motor_1 and one queue for motor_1

        # was expecting the queue to hold the time and the position but it looks like it has a maximum capacity of 6 digits 
        s0p = task_share.Share ('i', thread_protect = False, name = "Motor1_Position")
        s0t = task_share.Share ('i', thread_protect = False, name = "Motor1_Time")

        # the queue holds the right amount of data, just need a way to clean it up and read it
        q0 = task_share.Queue ('i', 1000, thread_protect = False, overwrite = False, name = "Motor1_Queue")

        # Intitialize the tasks for each motor controller using Task() 
        # assigned different priorities to see how it works, changing it back to the same value shouldnt affect it. 
        m1 = cotask.Task (motor_1, name = 'Motor 1', priority = 1, period = 40, profile = True, trace = False)
        m2 = cotask.Task (motor_2, name = 'Motor 2', priority = 1, period = 40, profile = True, trace = False)


        # add each task to the task list                     
        cotask.task_list.append (m1)
        cotask.task_list.append (m2)

        while True:
            cotask.task_list.pri_sched ()

        # A task which prints characters from a queue has automatically been
        # created in print_task.py; it is accessed by print_task.put_bytes()


        # Run the memory garbage collector to ensure memory is as defragmented as
        # possible before the real-time scheduler is started
        gc.collect ()

        # # Print a table of task data and a table of shared information data
        # print ('\n' + str (cotask.task_list) + '\n')
        # print (task_share.show_all ())
        # print (task1.get_trace ())
        # print ('\r\n')

    except KeyboardInterrupt:
        motor = motor_driver.MotorDriver('A10', 20000)
        motor.set_duty_cycle(0)

        motor_2 = motor_driver.MotorDriver('C1', 20000)
        motor_2.set_duty_cycle(0)