import serial_controller
import time

serial_port = serial_controller.Serial('/dev/cu.usbmodem205537A735412')

try:

    while True:
        x = serial_port.read()
        print (x)
except KeyboardInterrupt:
    serial_port.close()

    

