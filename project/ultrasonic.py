##
# Ultrasonic library for MicroPython's pyboard.
# Compatible with HC-SR04 and SRF04.
#
# Copyright 2018 - Sergio Conde Gómez <skgsergio@gmail.com>
# Copyright 2014 - Mithru Vigneshwara
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import pyb


class Ultrasonic:
    def __init__(self, trigger_pin, echo_pin):
        # WARNING: Don't use PA4-X5 or PA5-X6 as echo pin without a 1k resistor

        # Init trigger pin (out)
        self.trigger = pyb.Pin(trigger_pin, pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
        self.trigger.low()

        # Init echo pin (in)
        self.echo = pyb.Pin(echo_pin, pyb.Pin.IN, pyb.Pin.PULL_NONE)

    def distance_in_inches(self):
        return (self.distance_in_cm() * 0.3937)

    def distance_in_cm(self):
        start = 0
        end = 0

        micros = pyb.Timer(1, prescaler=83, period=0x3fffffff)
        micros.counter(0)
        # Send a 10us pulse
        self.trigger.high()
        pyb.udelay(10)
        self.trigger.low()

        # Wait for the pulse and calc its duration
        while self.echo.value() == 0:
            start = micros.counter()
        while self.echo.value() == 1:
            end = micros.counter()
        micros.deinit()

        # Calc the duration of the recieved pulse, divide the result by
        # 2 (round-trip) and divide it by 29 (the speed of sound is
        # 340 m/s and that is 29 us/cm).
        dist_in_cm = ((end - start) / 2) / 29

        return dist_in_cm
