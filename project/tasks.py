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

def ultraSonicDistanceTask():
    '''Is a bot too close? Run away. Is a bot almost too close? Run away. Can
    you see the bot? Run away. Running away is our bots survival tactic. If an
    enemy bot is detected within a 2 foot square area, our bot will turn an
    appropriate direction and continue running. The sensors are checked
    in order, so the front and rear sensors must be checked first. The sensors
    are sensitive, if anything is detected further than 30 inches away it is 
    disregarded and the bot can run on.'''

    US_1 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_1, P.US_DIST_ECHO_1)
    US_2 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_2, P.US_DIST_ECHO_2)
    US_3 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_3, P.US_DIST_ECHO_3)
    US_4 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_4, P.US_DIST_ECHO_4)

    OFF1 = const(0) # pylint: disable=undefined-variable
    ANALYZE_US = const(1)
    ANALYZE_FRONT = const(2)
    ANALYZE_REAR = const(3)
    ANALYZE_RIGHT = const(4)
    ANALYZE_LEFT = const(5)
    ANALYZE_BOT = const(6)
    DONT_ANALYZE_US = const(7)

    state = ANALYZE_US

    def eStop(state):
        if IR.getCommand() != C.START:
            state = OFF1
        yield(state)

    def checkForTurning(state):
        if turning.get() != 0:
            state = DONT_ANALYZE_US
        yield(state)

    def checkSensor(state, direction):
        if direction == 'front':
            uSensor = US_2
            share = us_front
        elif direction == 'left':
            uSensor = US_4
            share = us_left
        elif direction == 'right':
            uSensor = US_3
            share = us_right
        elif direction == 'rear':
            uSensor = US_1
            share = us_rear

        if state == ANALYZE_FRONT:
            eStop(state)

            # 2 feet is a safe range of detection, so 2.5 feet is safer.
            # Set different share values for directions detected.

            distance = uSensor.distance_in_inches()  
            ## FRONT US SENSOR
            # for a bot in closing position from the front, there is no time to 
            # turn the full 180 degrees. Turn 90 degrees and drive away
            if distance < 12:
                # print('FORWARD TRIG')
                # print(distance_front)
                level = 1
                share.put(level)
                # us_front.put(4)
            # for a bot in approaching position from the front, turn 180 degress
            # and drive away
            elif distance > 12 and distance < 18:
                # print('FORWARD TRIG')
                # print(distance_front)
                level = 2
                share.put(level)
                # us_front.put(3)

            # for a bot in detected position from the front, turn 180 degrees 
            # and drive away
            elif distance > 18 and distance < 24:
                # print('FORWARD TRIG')
                # print(distance_front)
                level = 3
                share.put(level)

            # if safe ahead, drive there
            elif distance > 24 and distance < 30:
                # print('safe ahead')
                level = 4
                share.put(level)

            elif distance > 30:
                # print('no threat')
                # print(distance_front)
                level = 0
                share.put(level)
            
            print(str('us_front: ') + str(us_front.get()))

            if share.get() != 0:
                curr_dir = state - 1
                curr_prox = share.get()
                if last_prox > curr_prox:
                    curr_prox = last_prox
                    curr_dir = last_dir
                else:
                    pass

            # print(str('incoming from: ') + str(us_current_dir.get()))
            # print(str('proximity: ') + str(us_current_prox.get()))
            
            checkForTurning(state)

            state = state + 1
            yield(state)
    while True:
        utime.sleep_ms(500)
        if state == ANALYZE_US:

            eStop(state)
            
            if turning.get() == 1:
                state = DONT_ANALYZE_US
                yield(state)
            
            state = ANALYZE_FRONT
            last_prox = 0
            last_dir = 0
            curr_dir = 0
            curr_prox = 0
            yield(state)

        if state == ANALYZE_FRONT:
            eStop(state)

            checkSensor(state, 'front')

        if state == ANALYZE_REAR:
            eStop(state)
            # REAR US SENSOR
            # for a bot in closing position from the rear, turn 90 degrees and drive away
            checkSensor(state, 'rear')
            
            

        if state == ANALYZE_RIGHT:
            eStop(state)
            ## RIGHT US SENSOR
            #for a bot in closing position from the right
           
            checkSensor(state, 'right')

        if state == ANALYZE_LEFT:
            eStop(state)

            # ## LEFT US SENSOR
            # for a bot in closing position from the left
            checkSensor(state, 'left')

        if state == ANALYZE_BOT:
            eStop(state)

            us_current_dir.put(curr_dir)
            us_current_prox.put(curr_prox)
            print(curr_dir)
            print(curr_prox)
            state = ANALYZE_FRONT
            yield(state)
            
        if state == DONT_ANALYZE_US:
            eStop(state)
            if turning.get == 0:
                state = ANALYZE_US
            yield(state)

        if state == OFF1:
            if IR.getCommand() == C.START:
                state = ANALYZE_US
            yield(state)