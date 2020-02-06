"""
Created on Wed Feb 05 09:14:00 2020

@author: Jacob Randall and Connor Bush

Initialize and read a motor encoder so the output is the current encoder position. 
"""
import pyb

class Encoder:
    ''' This class implements reading and resetting of the motor encoder '''
    def __init__ (self, pingroup):
        ''' Initializes timers for the encoder.
        @param pingroup Input of a character 'B' or 'C' representing 
        pingroups B6/B7 or C6/C7 on the cpu respectively '''
        
        print ('Setting up the encoder')

        if pingroup == 'B':
            ## If using the pingroup B, need to utilize timer 4
            ## If using pingroup B, implied that pin B6 uses channel 1 and pin B7 uses channel 2
            timer = 4
            PIN6 = pyb.Pin (pyb.Pin.board.PB6, mode = pyb.Pin.IN)
            PIN7 = pyb.Pin (pyb.Pin.board.PB7, mode = pyb.Pin.IN)
        elif pingroup == 'C':
            ## If using the pingroup C, need to utilize timer 8,
            ## If using pingroup B, implied that pin C6 uses channel 1 and pin C7 uses channel 2
            ## the other timers need to be saved for PWM motor control
            timer = 8
            PIN6 = pyb.Pin (pyb.Pin.board.PC6, mode = pyb.Pin.IN)
            PIN7 = pyb.Pin (pyb.Pin.board.PC7, mode = pyb.Pin.IN)
        else:
            ## throw exception
            return

        print ('Done Setting Up Encoder')
        ## Timer object specific to which pingroup the Encoder class
        ## was initialized with. Prescale set to zero, period set to 65535 (Hex FFFF)
        self.tim = pyb.Timer (timer, prescaler=0, period=0xFFFF)

        ## Channel 1 object specific to the pingroup selected
        self.ch_1 = self.tim.channel(1, pyb.Timer.ENC_A, pin = PIN6)
        ## Channel 2 object specific to the pingroup selected
        self.ch_2 = self.tim.channel(2, pyb.Timer.ENC_B, pin = PIN7)
        
        # initialize last value to 0 to start encoder at position 0.
        ## Last known count of the encoder
        self.last_value = 0

        # set current position to zero as well to ensure encoder is zeroed at start
        ## The current corrected position of the encoder
        self.current_position = 0
        
    def read (self):
        ''' This method reads the current position of the motor
        and returns it as a unsigned integer.
        @return Current position of motor 
        '''
        # read the encoder and save that value as the current value
        current_value = self.tim.counter()

        # delta is a signed value and is the difference between the current reading
        # the previous reading. If The value is positive, the motor was turning clockwise, if
        # negative, it was turning counterclockwise.
        delta = current_value - self.last_value

        if delta <= -32767:
            delta = current_value + (65535 - self.last_value)

        elif delta >= 32767:
            delta = -(self.last_value + (65535 - current_value))

        else:
            pass
        
        self.last_value = current_value
        self.current_position += delta
        return self.current_position

    def zero (self):
        ''' This method resets the encoders position to zero. 
        '''    
        self.current_position = 0