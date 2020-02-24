"""
@file infared.py
This module contains the Infared class which reads the IR reciever for 
start and stop signals to turn on the sumo bot.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""

from micropython import const, alloc_emergency_exception_buf
import pyb
import utime
import cotask
import task_share
import print_task
import busy_task

class Infared:
    '''This class reads the IR reciever for start and stop signals
    '''
    def __init__ (self, pin, timer, channel):
        ''' Initializes the infared receiver
        @param pin: pin is a pyb.Pin.board object
            for the interrupt pin that will detect interrupts
            from the IR reciever
        @param timer: timer is the timer the interrupt pin will use
        @param channel: channel is the channel the timer will use'''

        #----------------------------------------------------------------------#
        # Allocate memory so that exceptions raised in interrupt service
        # routines can generate useful diagnostic printouts
        alloc_emergency_exception_buf (100) #comment this line out after testing
        #----------------------------------------------------------------------#

        self.pin = pin
        self.timer = timer
        self.channel = channel

        # assign the pin as an input pin
        intPin = pyb.Pin (self.pin, pyb.Pin.IN)

        # Assign the timer a 16-bit period and a prescaler of 79 to collect
        # accurate timestamps. Prescaler of 79 to account for 80Mhz clock speed
        # to output counts as microseconds
        tim = pyb.Timer (self.timer, prescaler=79, period=0xFFFF)

        # set up the timer object to detect rising and fallingedges 
        self.ch1 = tim.channel(self.channel, pyb.Timer.IC, polarity = pyb.Timer.BOTH,
                            pin = intPin, callback = self.callback_fun)
        
        # A share to be used as a flag to indicate when a full set of
        # pulses has been read
        self.full_set_of_pulses = task_share.Share ('I', thread_protect = False,
                                                name = 'full_set_of_pulses')

        # A queue to be used as a buffer for interrupt timestamp data. Buffer
        # size is greater than full pulse count to account for repeat codes
        # that disrupt a full pulse set.
        self.ir_data = task_share.Queue ('I', 68, thread_protect = False,
                                        overwrite = False, name = "ir_data")

    ## using the timerObject from the interrupt,collect the timestamp data
    # from the IR signal.
    def callback_fun (self, timerObject):
        ''' This method is the callback function for the interrupt pin. It runs
        everytime an interrupt is detected and stores the time in microseconds
        to the queue.
        '''
        # if self.ir_data.num_in() == 68:
        #     # raise the full_set_of_pulses flag when the queue count gets to 68
        #     self.full_set_of_pulses.put(1, in_ISR=True)
        
        # continuously add timestamp data to the queue when an interrupt
        # is detected
        self.ir_data.put (timerObject.channel(self.channel).capture(),
                            in_ISR=True )

    def interpretIRdata (self):
        '''This method interprets a true full set of IR pulses (68 pulses)
        Note: the subdata list must be defined 
        Raises Exception if 2s complement of bytes are not accurate
        '''

        def assignBits (rangeLow, rangeHigh):
            '''This nested function interprets a range of pulse widths and
            determines if they are high or low bits, and then appends these
            bits to a list.
            @param rangeLow: rangeLow is the lowest number of the range
            @param rangeHigh: rangeHigh is the highest number of the range
            @return bits: bits is a list containing the integer value of bits
            '''

            bits = []
            for i in range (rangeLow,rangeHigh,2):
                total = self.subdata[i] + self.subdata[i+1]
                if total < 1300 and total > 1000:
                    bits.append(0)
                elif total > 2100 and total < 2400:
                    bits.append(1)
                else:
                    print('did not interpret pulse properly')
            return bits
        
        def assignBytes (bits, decimal=False):
            '''This nested function interprets a list of bits and converts them
            into a formatted binary byte.
            @param bits: bits is a list of bits
            @param decimal: decimal is boolean, set to true if the
                decimal Value is required
            @return bytes: bytes is a formatted string of bits
            @return decimalValue: decimalValue is the decimal value of the byte
                or bytes
            '''
            decimalValue = 0
            for n in range (len(bits)):
                decimalValue |= bits[n] << n
            
            formattedByte = '{:#010b}'.format(decimalValue)
            
            if decimal == True:
                return formattedByte, decimalValue
            else:
                return formattedByte

        # initialize the rawBits list to empty
        rawBits = assignBits (2,66)
        addressBits = assignBits (2,18)
        naddressBits = assignBits (18,34)
        commandBits = assignBits (34,50)
        ncommandBits = assignBits (50,66)


        rawBytes = assignBytes(rawBits)
        addressByte, addressByteD = assignBytes(addressBits, True)
        naddressByte = assignBytes(naddressBits)
        commandByte, commandByteD = assignBytes(commandBits, True)
        ncommandByte = assignBytes(ncommandBits)

        if int(addressByte) ^  int(naddressByte) == 255:

            if int(commandByte) ^ int(ncommandByte) == 255:
                return ('--------------- New Packet ---------------\n'
                        + '  RAW:  ' + rawBytes + '\n'
                        + ' ADDR:  ' + addressByte + '\n'
                        + 'nADDR:  ' + naddressByte + '\n'
                        + '  CMD:  ' + commandByte + '\n'
                        + ' nCMD:  ' + ncommandByte + '\n'
                        + '\n'
                        + 'Address (Decimal):  ' + str(addressByteD) + '\n'
                        + 'Command (Decimal):  ' + str(commandByteD) + '\n'
                        + '------------------------------------------')

            else:
                print('2s complement of commandByte is not accurate')
                return False
        else:
            print('2s complement of addressByte is not accurate')
            return False

    def readInfaredSensorTask (self):
        ''' This method reads the data stored in the queue and runs the
        interpretIRdata function when a true full set of pulses is found.
        '''

        def interpretRawIRdata ():
            ''' This nested function interprets the raw data and determines
            pulse widths. These pulse widths are appended to the rawBits list.
            Note: The data list must be initialized before calling this
                function
            @return: Returns rawBits if successful, returns False if 
                unsuccessful
            '''
            rawData = self.data
            self.data = []
            rawBits = []
            start = False
            # find the difference between edges 
            for i in range (0,len(rawData) - 1, 2):

                delta = rawData[i+2] - rawData[i]
                
                if delta < 0:
                    delta = delta + 65535
                if start:
                    while len(rawBits) < 32:
                        if delta < 1300 and delta > 1000:
                            rawBits.append(0)
                            print(0)
                        elif delta > 2100 and delta < 2400:
                            rawBits.append(1)
                            print(``)
                        else:
                            print('not a valid bit. Delta = ' + str(delta))
                            rawBits = []
                            start = False
                            continue
                    if len(rawBits) == 32:
                        return rawBits
                    else:
                        print('somehow got here')
                        return False
                    
                if delta > 13000 and delta < 15000:
                    print('start')
                    start = True
                    continue
                else:
                    continue
 
        # Initialization for this task.
        # Initialize data and subdata lists to empty
        # Initialize the full_set_of_pulses flag to 0
        self.data = []
        self.subdata = []

        while True:
            while len(self.data) < 68:
                self.data.append(self.ir_data.get())

            successfulInterpretation = interpretRawIRdata()

            while not successfulInterpretation:
                successfulInterpretation = interpretRawIRdata()
