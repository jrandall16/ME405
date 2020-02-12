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

# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
alloc_emergency_exception_buf (100)

# Declare some constants to make state machine code a little more readable.
# This is optional; some programmers prefer to use numbers to identify tasks

def motor_1 ():
    motor = motor_driver.MotorDriver('A10', 20000)

    # call class Controller()
    ctr = controller.Controller(0.01, 16000, 30)

    ## define the encoder that is used to read the motor position
    encB = enc.Encoder('B')

    while True:
        motor.set_duty_cycle(ctr.outputValue(encB.read()))

        ## need to figure out print_task
        #shares.print_task.put(encB.read())

        print_task.put_bytes (bytes(encB.read()))

        yield (0)

def motor_2 ():
    motor_2 = motor_driver.MotorDriver('C1', 20000)

    # call class Controller()
    ctr_2 = controller.Controller(0.01, 16000, 30)

    ## define the encoder that is used to read the motor position
    encC = enc.Encoder('C')
    while True:
        motor_2.set_duty_cycle(ctr_2.outputValue(encC.read()))
        
        print_task.put_bytes (bytes(encC.read()))
        yield (0)
# =============================================================================

if __name__ == "__main__":
    try:
        print ('\033[2JTesting scheduler in cotask.py\n')

        # Create a share and some queues to test diagnostic printouts
        share0 = task_share.Share ('i', thread_protect = False, name = "Share_0")
        q0 = task_share.Queue ('B', 6, thread_protect = False, overwrite = False,
                            name = "Queue_0")
        q1 = task_share.Queue ('B', 8, thread_protect = False, overwrite = False,
                            name = "Queue_1")

        # Create the tasks. If trace is enabled for any task, memory will be
        # allocated for state transition tracing, and the application will run out
        # of memory after a while and quit. Therefore, use tracing only for 
        # debugging and set trace to False when it's not needed
        task1 = cotask.Task (motor_1, name = 'Motor 1', priority = 1, 
                            period = 100, profile = True, trace = False)

        task2 = cotask.Task (motor_2, name = 'Motor 2', priority = 1, 
                            period = 100, profile = True, trace = False)

        cotask.task_list.append (task1)
        cotask.task_list.append (task2)

        # A task which prints characters from a queue has automatically been
        # created in print_task.py; it is accessed by print_task.put_bytes()



        
        # Create a bunch of silly time-wasting busy tasks to test how well the
        # scheduler works when it has a lot to do
        # for tnum in range (10):
        #     newb = busy_task.BusyTask ()
        #     bname = 'Busy_' + str (newb.ser_num)
        #     cotask.task_list.append (cotask.Task (newb.run_fun, name = bname, 
        #         priority = 0, period = 400 + 30 * tnum, profile = True))

        # Run the memory garbage collector to ensure memory is as defragmented as
        # possible before the real-time scheduler is started
        gc.collect ()

        # Run the scheduler with the chosen scheduling algorithm. Quit if any 
        # character is sent through the serial port
        vcp = pyb.USB_VCP ()
        while not vcp.any ():
            cotask.task_list.pri_sched ()

        # Empty the comm port buffer of the character(s) just pressed
        vcp.read ()

        # Print a table of task data and a table of shared information data
        print ('\n' + str (cotask.task_list) + '\n')
        print (task_share.show_all ())
        print (task1.get_trace ())
        print ('\r\n')

    except KeyboardInterrupt:
        motor = motor_driver.MotorDriver('A10', 20000)
        motor.set_duty_cycle(0)

        motor_2 = motor_driver.MotorDriver('C1', 20000)
        motor_2.set_duty_cycle(0)