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

# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
alloc_emergency_exception_buf (100)

# Declare some constants to make state machine code a little more readable.
# This is optional; some programmers prefer to use numbers to identify tasks
GOING = const (0)
STOPPED = const (1)


def task1_fun ():
    """ @brief   Demonstration task which changes state periodically.
        @details This function implements Task 1, which toggles twice every
        second in a way which is only slightly silly.  
    """
    state = STOPPED
    counter = 0

    while True:
        if state == GOING:
            print_task.put_bytes (b'GOING\r\n')
            state = STOPPED

        elif state == STOPPED:
            print_task.put_bytes (b'STOPPED\r\n')
            state = GOING

        else:
            raise ValueError ('Illegal state for task 1')

        # Periodically check and/or clean up memory
        counter += 1
        if counter >= 60:
            counter = 0
            print_task.put_bytes (' Memory: {:d}'.format (gc.mem_free ()))

        yield (state)


def task2_fun ():
    """ @brief   Demonstration task which prints weird messages.
        @details This function implements Task 2, a task which is somewhat
                 sillier than Task 1 in that Task 2 won't shut up. Also, 
                 one can test the relative speed of Python string manipulation
                 with memory allocation (slow) @a vs. that of manipulation of 
                 bytes in pre-allocated memory (faster).
    """
    t2buf = bytearray ('<.>')         # Allocate memory once, then just use it
    char = ord ('a')

    # Test the speed of two different ways to get text out the serial port
    while True:
        # Choose True or False below to select which method to try
        if False:
            # (1) Allocate a Python string - this is slower, around 2 ms
            shares.print_task.put ('<' + chr (char) + '>')
        else:
            # (2) Put a character into an existing bytearray; this requires 
            # no memory allocation and runs faster
            t2buf[1] = char
            print_task.put_bytes (t2buf)

        char += 1
        if char > ord ('z'):
            char = ord ('a')
        yield (0)


# =============================================================================

if __name__ == "__main__":

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
    task1 = cotask.Task (task1_fun, name = 'Task_1', priority = 1, 
                         period = 1000, profile = True, trace = False)
    task2 = cotask.Task (task2_fun, name = 'Task_2', priority = 2, 
                         period = 100, profile = True, trace = False)
    cotask.task_list.append (task1)
    cotask.task_list.append (task2)

    # A task which prints characters from a queue has automatically been
    # created in print_task.py; it is accessed by print_task.put_bytes()

    # Create a bunch of silly time-wasting busy tasks to test how well the
    # scheduler works when it has a lot to do
    for tnum in range (10):
        newb = busy_task.BusyTask ()
        bname = 'Busy_' + str (newb.ser_num)
        cotask.task_list.append (cotask.Task (newb.run_fun, name = bname, 
            priority = 0, period = 400 + 30 * tnum, profile = True))

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

