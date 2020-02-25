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
import task_share

class Infared:
    '''This class reads the IR reciever for start and stop signals
    '''
    def __init__ (self, pin, timer, channel):
        ''' Initializes the infared receiver
        @param pin: pin is a pyb.Pin.board object
            for the interrupt pin that will detect interrupts
            from the IR reciever
        @param timer: timer is the timer the interrupt pin will use
        @param channel: channel is the channel the timer will use
        '''

        #----------------------------------------------------------------------#
        # Allocate memory so that exceptions raised in interrupt service
        # routines can generate useful diagnostic printouts
        alloc_emergency_exception_buf (100) #comment this line out after testing
        #----------------------------------------------------------------------#

        # assign the pin as an input pin
        intPin = pyb.Pin (pin, pyb.Pin.IN)
        
        ## channel is the channel the timer will use, specified by the function
        # parameter. Has to be brought to the Class scope because it is used in
        # the irISR callback function
        self.channel = channel
        # Assign the timer a 16-bit period and a prescaler of 79 to collect
        # accurate timestamps. Prescaler of 79 to account for 80Mhz clock speed
        # to output counts as microseconds
        tim = pyb.Timer (timer, prescaler=79, period=0xFFFF)

        # set up the timer object to detect rising and fallingedges 
        tim.channel(channel, pyb.Timer.IC, polarity = pyb.Timer.BOTH,
                            pin = intPin, callback = self.irISR)

        # A queue to be used as a buffer for interrupt timestamp data. Buffer
        # size is greater than full pulse count to account for repeat codes
        # that disrupt a full pulse set.
        self.ir_data = task_share.Queue ('I', 140, thread_protect = False,
                                        overwrite = False, name = "ir_data")


    def irISR (self, timerObject):
        ''' This method is the callback function for the interrupt pin. It runs
        everytime an interrupt is detected and stores the time in microseconds
        to the queue. This callback function is kept as short as possible to
        limit the time it interrupts the code.
        '''

        # using the timerObject from the interrupt,collect the timestamp data
        # from the IR signal.
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
            # initialize decimalValue to 0
            decimalValue = 0

            # for every bit in rawBits:
            # perform an or operation on the bit and then add it to the existing
            # decimalValue
            # then shift left the decimalValue by index of that bit
            for n in range (len(bits)):
                decimalValue |= bits[n] << n

            # convert the decimalValue to a binary string with prefix 0b
            formattedByte = '{:#010b}'.format(decimalValue)

            # if decimal was specified, return both
            if decimal == True:
                return formattedByte, decimalValue
            # if not, return just the formattedByte
            else:
                return formattedByte

        # note that slice position is not index position, see example below
        #                 +---+---+---+---+---+---+
        #                 | P | y | t | h | o | n |
        #                 +---+---+---+---+---+---+
        # Slice position: 0   1   2   3   4   5   6
        # Index position:   0   1   2   3   4   5
        # slice the rawBits list into 4 bytes as follows
        addressBits = rawBits[0:8]
        naddressBits = rawBits[8:16]
        commandBits = rawBits[16:24]
        ncommandBits = rawBits[24:32]

        # get the formatted Byte and decimcal value if specified
        rawBytes = assignBytes(rawBits)
        addressByte, addressByteD = assignBytes(addressBits, True)
        naddressByte = assignBytes(naddressBits)
        commandByte, commandByteD = assignBytes(commandBits, True)
        ncommandByte = assignBytes(ncommandBits)

        # return a formatted string as follows
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
        
        # grab the data list from the class scope and assign to rawData
        # this is done to preserve the data list incase it needs to be
        # mutated
        rawData = self.data

        # initialize rawBits list
        rawBits = []

        # init start flag to False
        start = False

        # find the difference between falling edges 
        for i in range (0,len(rawData) - 2, 2):
            delta = rawData[i+2] - rawData[i]
            
            # adjust data if overflowed
            if delta < 0:
                delta = delta + 65535

            # check if start flag is True
            if start:

                # check if binary low
                if delta < 1300 and delta > 1000:
                    rawBits.append(0)
                # check if binary high
                elif delta > 2100 and delta < 2400:
                    rawBits.append(1)
                else:
                    # if somehow neither, clear the rawBits list
                    # and set start flag to False then fall out to
                    # next if statement
                    print('not a valid bit. Delta = ' + str(delta))
                    rawBits = []
                    start = False

                # if we have a full set of bits, clear the data list
                # and return the rawBits list   
                if len(rawBits) == 32:
                    self.data = []
                    return rawBits
            # check for start signal
            if delta > 13000 and delta < 15000:
                # if the start signal did not occur at the beginning
                # of the list, then delete all the data leading up to
                # it and break out of for loop to fall out and be
                # re-evaluated
                if i:
                    del self.data[0:i]
                    break

                # otherwise set start flag and resume for loop
                else:
                    start = True
                    continue
            # if no start signal, check for a repeat signal
            elif delta > 11000 and delta < 12500:
                # if found, delete all the data associated with the repeat
                # signal, then return 1
                del self.data[i:i+4]
                return 1

            # the maximum pulse is ~9ms, so anything greater than that
            # is invalid data. 
            elif self.data[i+1] - self.data[i] > 10000:
                # if invalid data, delete that pulse and break out of for
                # loop to fall out and be re-evaluated
                del self.data[i:i+1]
                break
            # if we got this far then the signal was good, so continue
            # through the for loop
            else:
                continue
        # if we fall out of the for loop without returning anything,
        # then the data needs to refill to a length of 68 and then
        # be re-evaluated. Return False
        return False

    def readInfaredSensorTask (self):
        ''' This method reads the data stored in the queue and runs the
        interpretIRdata function when a true full set of pulses is found.
        '''

        # Initialization for this task.
        ## Data is a class scoped list that is filled with timestamps
        # from the ir_data queue
        self.data = []

        # run consistently (will have to yield for other tasks)
        while True:
            while len(self.data) < 68:
                # append timestamps to the data list until it has 68
                # timestamps
                self.data.append(self.ir_data.get())
            
            # successfulTranslate is set to the value returned from
            # the translateRawIRdata function
            successfulTranslate = self.translateRawIRdata()
            
            # if translateRawIRdata returns the rawBits list
            if type(successfulTranslate) == list:
                # run the formattedBytes function to return the 
                # formatted string
                formattedBytes = self.formattedBytes(successfulTranslate)
                print(formattedBytes)

            # if translateRawIRdata returns 1 (repeat code)
            elif successfulTranslate == 1:
                # print the last recieved formatted string
                print(formattedBytes)
            
            # if translateRawIRdata returns False, re-evaluate the data
            # and then break out of the while loop to start at the top
            # and be retested. Repeat until a set of rawBits is found
            while not successfulTranslate:
                successfulTranslate = self.translateRawIRdata()
                break

