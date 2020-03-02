# -*- coding: utf-8 -*-
"""
@file lineFollower.py
This module contains the LineFollower class which uses Pololu QRT Reflective
sensors to detect differences in reflectivity. This difference is then used
to determine whether a line is present (white/reflective) or if there is no
line present (dark/not reflective)

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""

import pins
import utime  # pylint: disable=import-error


class LineFollower:
    '''This class detects when a white line is present on a black surface and
    uses an algorithm to send the robot directins for which way to turn.'''

    def __init__(self, enablePin, pinArray, waitTime):
        '''This method initializes the LineFollower class with the given
        parameters.

        @ param enablePin: enablePin is the pin used to control the power
            supplied to the sensors
        @ param pinArray: pinArray is an array of pyb.Pin.board pin objects
            that are mapped to the sensors. The first item in the array being
            the far left sensor and the last item being the far right
            sensor.
        @param waitTime: waitTime is the time in us that the robot will check
            the input of the sensor pin after driving it high. See this
            website for more details: https://www.pololu.com/product/1419
        '''

        # qrtEnable is the enable pin, set to output because a signal has to be
        # sent to this pin in order to turn the array of sensors on
        self.qrtEnable = pins.output(enablePin)

        # qrtArray is the array of pyb.Pin.board objects that correlate with
        # the physical array of sensors.
        self.qrtArray = pinArray

        # the time in us that the robot will check
        # the input of the sensor pin after driving it high. See this
        # website for more details: https: // www.pololu.com/product/1419
        self.waitTime = waitTime

    def getSensorOutput(self):
        '''This method reads the array of sensors and returns an array of
        binary numbers, 1s representing a non-reflective object and 0s
        representing a reflective object(line).'''

        def runSensors(sensorArray):
            '''This nested function runs the sensors by setting them as output
            pins and driving the pins high. It then sets the pins as inputs and
            appends the pin objects to a list.

            @param sensorArray: sensorArray is the QRTsensor array
            @return inputArray the array of input pins
            '''

            inputArray = []
            for n in range(len(sensorArray)):
                pin = pins.output(sensorArray[n])
                sensorArray[n].high()
                pin = pins.input(sensorArray[n])
                inputArray.append(pin)
            return inputArray

        def readsensors(inputArray, waitTime):
            '''This nested function runs the sensors by setting them as output
            pins and driving the pins high. It then sets the pins as inputs and
            appends the pin objects to a list.

            @param sensorArray: sensorArray is the QRTsensor array
            @param waitTime: waitTime is the time in us that the function should
                wait for after running
            @return inputArray the array of input pins
            '''

            sensorOutput = []

            for n in range(len(inputArray)):
                sensorOutput.append(inputArray[n].value())
                # wait for the specified wait time after all of the sesnors
                # have been analyzed
                if n == len(inputArray):
                    utime.sleep_us(waitTime)
            return sensorOutput

        # provide power to the sensor array
        self.qrtEnable.high()

        # set pins high and then reset to input
        inputArray = runSensors(self.qrtArray)

        # read values from sensors and store in a list
        sensorOutput = readsensors(inputArray, self.waitTime)

        # kill power to the array
        self.qrtEnable.low()

        return sensorOutput

    def analyzeSensorData(self):
        data = self.getSensorOutput()
        leftSum = 0
        rightSum = 0
        left = False
        right = False
        for i in data[0:3]:
            rightSum += i
        for i in data[3:6]:
            leftSum += i

        turn = 0
        if leftSum <= 1:
            left = True
            # turn right because the edge was detected on the left side
            turn = 1
        if rightSum <= 1:
            right = True
            # turn left because the edge was detected on the right side
            turn = 2
        if left and right:
            # turn 180 because the full edge was detected
            turn = 3

        return turn
