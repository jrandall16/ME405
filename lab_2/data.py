# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 08:59:23 2020

@author: melab15
"""

import pyb
import encoder
import task_share

class queue:
    ''' This class employs class task_share and encoder to process data received
    from the motor used in ME405 Lab. Time and position are the data taken from
    the motor. The data are stored in a queue and plotted to determine the 
    motor time constant and steady state gain.
    '''
    
    def read():
        ''' Read the encoder position and store it 
        '''
        
       task_share.queue.__init__('f', size = 1000, name = 'motor data') 
       