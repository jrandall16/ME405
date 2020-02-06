"""
Created on Wed Feb 05 09:14:00 2020

@author: Jacob Randall and Connor Bush

Run the motor controller on the Nucleo board. The motor will reach the position, Kp and steady state gain defined when initiallizing the Controller class. Emplot class MotorDriver to send the PWM signal to the motor and reach the desired position. 
"""
import encoder as enc
import motor_driver
import utime
import controller

# call class MotorDriver()
motor = motor_driver.MotorDriver()

# call class Controller()
ctr = controller.Controller(0.05, 16000, 30)

## define the encoder that is used to read the motor position
encB = enc.Encoder('B')

# initiate a try block with exception for emergency stop by keyboard interupt
try:
    print ('firstline')
    while True:
        # set the duty cycle to the output of controller function outputValue() using the current position of the encoder to determine the actuation signal
        motor.set_duty_cycle(ctr.outputValue(encB.read()))

        # print the data into the terminal to be read by the pc
        print (str(encB.read()) + ',' + str(utime.ticks_ms()))

        # print data every 10 milliseconds
        utime.sleep_ms(10)



# set duty cycle of the motor to 0 if a keyboard interput is thrown
except KeyboardInterrupt:
    motor.set_duty_cycle(0)
    
    


    
    
    

