"""
@file infared.py
This module contains the Infared class which reads the IR reciever for 
start and stop signals to turn on the sumo bot.

@author Jacob Randall and Connor Bush
@date Sat Feb  22 10:59:12 2017
"""

from micropython import const, alloc_emergency_exception_buf  # pylint: disable=import-error
import pyb  # pylint: disable=import-error
import utime  # pylint: disable=import-error
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

    def formattedBytes (self, rawBits):
        '''This method interprets a set of 32 bits into bytes
        @param rawBits: A list of 32 rawBits
        @return returns a formatted string of the 4 named bytes if successful,
            returns False if unsuccessful
        '''
        
        def assignBytes (bits, decimal=False):
            '''This nested function interprets a list of bits and converts them
            into a formatted binary byte.
            @param bits: bits is a list of bits
            @param decimal: decimal is boolean, set to true if the
                decimal Value is required
            @return bytes, decimalValue: bytes is a formatted string of bits
                decimalValue is the decimal value of the byte or bytes
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
        addressBits = rawBits[0:7]
        naddressBits = rawBits[8:15]
        commandBits = rawBits[16:23]
        ncommandBits = rawBits[24:31]


        rawBytes = assignBytes(rawBits)
        addressByte, addressByteD = assignBytes(addressBits, True)
        naddressByte = assignBytes(naddressBits)
        commandByte, commandByteD = assignBytes(commandBits, True)
        ncommandByte = assignBytes(ncommandBits)

        if int(addressByte) ^  int(naddressByte) == 255:

            if int(commandByte) ^ int(ncommandByte) == 255:
                # return ('--------------- New Packet ---------------\n'
                #         + '  RAW:  ' + rawBytes + '\n'
                #         + ' ADDR:  ' + addressByte + '\n'
                #         + 'nADDR:  ' + naddressByte + '\n'
                #         + '  CMD:  ' + commandByte + '\n'
                #         + ' nCMD:  ' + ncommandByte + '\n'
                #         + '\n'
                #         + 'Address (Decimal):  ' + str(addressByteD) + '\n'
                #         + 'Command (Decimal):  ' + str(commandByteD) + '\n'
                #         + '------------------------------------------')
                print('good packet')
            else:
                print('2s complement of commandByte is not accurate')
                # return False
        else:
            print('2s complement of addressByte is not accurate')
            # return False

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
        
    def translateRawIRdata (self):
        ''' This nested function interprets the raw data and determines
        pulse widths. These pulse widths are appended to the rawBits list.
        Note: The data list must be initialized before calling this
            function
        @return: Returns rawBits as a list of 32 bits if successful,
            returns False if unsuccessful
        '''
        rawData = self.data
        rawBits = []
        start = False
        # find the difference between edges 
        for i in range (0,len(rawData) - 2, 2):
            delta = rawData[i+2] - rawData[i]
            
            if delta < 0:
                delta = delta + 65535
            if start:
                if delta < 1300 and delta > 1000:
                    rawBits.append(0)
                elif delta > 2100 and delta < 2400:
                    rawBits.append(1)
                else:
                    print('not a valid bit. Delta = ' + str(delta))
                    rawBits = []
                    start = False
                if len(rawBits) == 32:
                    self.data = []
                    return rawBits
                
            if delta > 13000 and delta < 15000:
                if i:
                    del self.data[0:i]
                    print('deleted data')
                    break
                else:
                    print('start')
                    start = True
                    continue
            elif delta > 11000 and delta < 12500:
                del self.data[i:i+4]
                print('repeat')
                break
            elif self.data[i+1] - self.data[i] > 10000:
                del self.data[i:i+1]
                print('large gap')
                break
            else:
                continue

    def readInfaredSensorTask (self):
        ''' This method reads the data stored in the queue and runs the
        interpretIRdata function when a true full set of pulses is found.
        '''

        # Initialization for this task.
        # Initialize data and subdata lists to empty
        # Initialize the full_set_of_pulses flag to 0
        self.data = []
        self.subdata = []

        while True:
            while len(self.data) < 68:
                self.data.append(self.ir_data.get())

            successfulTranslate = self.translateRawIRdata()

            while not successfulTranslate:
                successfulTranslate = self.translateRawIRdata()
                break

            if successfulTranslate:
                formattedBytes = self.formattedBytes(successfulTranslate)
                print(formattedBytes)
            else:
                print('else')
