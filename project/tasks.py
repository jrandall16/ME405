# -*- coding: utf-8 -*-
"""
@file tasks.py
This module contains shares, queues, and tasks to be used in the
main robot code.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""

import pyb # pylint: disable=import-error
import utime # pylint: disable=import-error
from micropython import const # pylint: disable=import-error
import scheduler_files.cotask as cotask
import scheduler_files.task_share as task_share
import scheduler_files.print_task as print_task
import scheduler_files.busy_task as busy_task
import motors
import constant
import pins

## emergency is a transition variable that indicates the motor needs to stop
emergency = task_share.Share ('I', thread_protect = False,
                                name = "emergency stop")

## desiredSpeed is the speed the controller is trying to reach
desiredSpeed = task_share.Share ('I', thread_protect = False,
                                    name = "desired speed")

## currentSpeed is the current speed read from the encoder
currentSpeed = task_share.Share ('I', thread_protect = False,
                                    name = "current speed")

## level is the magnitude of ouptput DC voltage to the motor
level = task_share.Share ('I', thread_protect = False, name = "DC level")

## direction is the direction the motor is turning
# 1 -> forward
# -1 -> backwards
direction = task_share.Share ('I', thread_protect = False,
                                name = "drive direction")



## variable indicating a turn.
# 1 -> CW90    -1 -> CCW90
# 2 -> CW180    -2 -> CCW180
# 3 -> CW270    -3 -> CCW270
# 4 -> CW360    -4 -> CCW360
turn = task_share.Share ('I', thread_protect = False, name = "turn")


###--------------------------------------------------------------------------###


## Define a task to drive motor_1
def motor_1_driver ():
    ''' This task drives motor_1 using input parameters level and direction.
    This task has 3 states. 
    State 1 runs the motor
    State 2 runs the motor to turn the bot a set amount of degrees
    State 3 stops the motor
    '''

    RUN = const(1)
    TURN = const(2)
    STOP = const(3)
    
    # init motorDriver
    motor = motors.MotorDriver(pins.M1DIR, pins.M1PWM,
                                constant.MOT_PWM_TIMER, constant.MOT1_PWM_CH,
                                constant.MOT_FREQ)

    state = STOP
    while True:
        if state == RUN:
            # if emergency, transition to STOP state
            if emergency:
                motor.set_duty_cycle(0,0)
                state = STOP
            # if turn, transition to TURN state
            elif turn:
                state = TURN
            # if none, 
            else:
                motor.set_duty_cycle(level, direction)
                state = RUN
            yield(state)

        if state == TURN:
            motor.turn(turn) 
            # always transition to RUN state
            state = RUN
            yield(state)

        if state == STOP:
            # if emergency is cleared, return to RUN state
            if not emergency:
                state = RUN
            # if emergency is not cleared,
            # remain in STOP state and set PWM signal to 0.
            else:
                motor.set_duty_cycle(0,0)
                state = STOP
            yield(state)

## Define a task to control motor_1
def motor_1_controller ():
    ''' This task controls motor_1 using input parameters Kp,
    desiredSpeed, and currentSpeed. This task has 2 states.
    State 1 runs the controller with the current input parameters
    State 2 runs the controller with the necessary input parameters to turn
    State 3 stops the motor if emergency
    '''
    RUN = const(1)
    TURN = const(2)
    STOP = const(3)

    ## call class Controller()
    controller = motors.MotorController(constant.KP)
    state = STOP
    while True:
        if state == RUN:
            # if emergency, transition to STOP state
            if emergency:
                state = STOP
            # if turn, transition to TURN state
            elif turn:
                state = TURN
            # if none, continue in RUN state with the input values
            else:
                controller.outputDC(currentSpeed)
                controller.setDesiredSpeed(desiredSpeed)
                state = RUN

            yield(state)


        # make a turn specified by the shares
        # if state == TURN:
        #     if cw90deg:
        #         controller.outputSpeed(currentSpeed)
        #         controller.setKp(Kp)
        #         controller.setDesiredSpeed(desiredSpeed)
        #     elif cw180deg:
        #         controller.outputSpeed(currentSpeed)
        #         controller.setKp(Kp)
        #         controller.setDesiredSpeed(desiredSpeed)
        #     elif cw360deg:
        #         controller.outputSpeed(currentSpeed)
        #         controller.setKp(Kp)
        #         controller.setDesiredSpeed(desiredSpeed)
        #     elif ccw90deg:
        #         controller.outputSpeed(currentSpeed)
        #         controller.setKp(Kp)
        #         controller.setDesiredSpeed(desiredSpeed)
        #     elif ccw90deg:
        #         controller.outputSpeed(currentSpeed)
        #         controller.setKp(Kp)
        #         controller.setDesiredSpeed(desiredSpeed)
        #     elif ccw90deg:
        #         controller.outputSpeed(currentSpeed)
        #         controller.setKp(Kp)
        #         controller.setDesiredSpeed(desiredSpeed)

            # always transition to RUN state
            state = RUN
            yield(state)

        if state == STOP:
            # if emergency is cleared, transition to RUN state
            if not emergency:
                state = RUN

            # if emergency is not cleared, set desiredSpeed to 0
            # and remain in STOP state
            else:
                controller.setDesiredSpeed(0)
                state = STOP
            yield(state)

## Define a task to read the encoder on motor_1
def motor_1_encoder():
    ''' This task runs the motor_1 encoder using no input parameters
    encoderpinA, channelA, encoderpinB, channelB, and timer.
    This task has 2 states.
    State 1: This state reads the encoder and outputs the current speed
    State 2: This state resets the encoder to zero
    '''
    READ = const(1)
    RESET = const(2)

    ## call class Encoder()
    encoder = motors.Encoder (pins.ENC1A, constant.ENC1A_CH, pins.ENC1B,
                                constant.ENC1B_CH, constant.ENC1_TIMER)

    state = RESET
    while True:
        if state == READ:
            if emergency:
                state = RESET
            else:
                encoder.read()
                state = READ
        if state == RESET:
            if not emergency:
                state = READ
                encoder.zero()
            else:
                state = RESET