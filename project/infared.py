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
import cotask


class Infared:
    '''This class reads the IR reciever for start and stop signals
    '''

    def __init__(self, pin, timer, channel):
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
        # comment this line out after testing
        alloc_emergency_exception_buf(100)
        #----------------------------------------------------------------------#

        # assign the pin as an input pin
        intPin = pyb.Pin(pin, pyb.Pin.IN)

        # channel is the channel the timer will use, specified by the function
        # parameter. Has to be brought to the Class scope because it is used in
        # the irISR callback function
        self.channel = channel
        # Assign the timer a 16-bit period and a prescaler of 79 to collect
        # accurate timestamps. Prescaler of 79 to account for 80Mhz clock speed
        # to output counts as microseconds
        tim = pyb.Timer(timer, prescaler=79, period=0xFFFF)

        # set up the timer object to detect rising and fallingedges
        tim.channel(channel, pyb.Timer.IC, polarity=pyb.Timer.BOTH,
                    pin=intPin, callback=self.irISR)

        # A queue to be used as a buffer for interrupt timestamp data. Buffer
        # size is greater than full pulse count to account for repeat codes
        # that disrupt a full pulse set.
        self.ir_data = task_share.Queue('I', 200, thread_protect=False,
                                        overwrite=False, name="ir_data")
        # Data is a class scoped list that is filled with timestamps
        # from the ir_data queue
        self.data = []

        self.go = task_share.Share('I', thread_protect=False, name="go")
        self.go.put(0)

        self.task = cotask.Task(self.readInfaredSensorTask,
                                name='Infared Reading Task',
                                priority=0, profile=True, trace=False)

    def irISR(self, timerObject):
        ''' This method is the callback function for the interrupt pin. It runs
        everytime an interrupt is detected and stores the time in microseconds
        to the queue. This callback function is kept as short as possible to
        limit the time it interrupts the code.
        '''

        # using the timerObject from the interrupt,collect the timestamp data
        # from the IR signal.

        if self.ir_data.num_in() >= 68:
            self.task.go()
        if not self.ir_data.full():
            self.ir_data.put(timerObject.channel(self.channel).capture(),
                             in_ISR=True)

    def formattedBytes(self, rawBits):
        '''This method interprets a set of 32 bits into bytes
        @param rawBits: A list of 32 rawBits
        @return returns a formatted string of the 4 named bytes if successful,
            returns False if unsuccessful
        '''

        def assignBytes(bits, decimal=False):
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
            for n in range(len(bits)):
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

    def translateRawIRdata(self):
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

        # find the difference between falling edges
        for i in range(0, len(rawData) - 2, 2):
            delta = rawData[i+2] - rawData[i]
            # adjust data if overflowed
            if delta < 0:
                delta = delta + 65535
            print('fun' + str(delta))
            if delta > 13300 and delta < 13700:
                pass
            # check if binary low
            elif delta < 1300 and delta > 1000:
                rawBits.append(0)
            # check if binary high
            elif delta > 2100 and delta < 2400:
                rawBits.append(1)
            else:
                # if somehow neither, clear the rawBits list
                # and set start flag to False then fall out to
                # next if statement
                print('not a valid bit. Delta = ' + str(delta))
                self.clearData()
                break

            # if we have a full set of bits, clear the data list
            # and return the rawBits list
            if len(rawBits) == 32:
                self.clearData()
                return rawBits

        return False

    def clearData(self):
        self.data = []

    def appendData(self):
        self.data.append(self.ir_data.get())

    def readInfaredSensorTask(self):
        ''' This method reads the data stored in the queue and runs the
        interpretIRdata function when a true full set of pulses is found.
        '''

        self.clearData()
        # Initialization for this task.
        while True:
            # while len(self.data) < 68:
            # append timestamps to the data list until it has 68
            # timestamps
            successfulTranslate = False
            if len(self.data) == 68:
                leading_pulse = self.data[2] - self.data[0]
                if leading_pulse < 0:
                    leading_pulse = leading_pulse + 65535
                trailing_pulse = self.data[67] - self.data[66]
                if trailing_pulse < 0:
                    trailing_pulse = trailing_pulse + 65535
                print(leading_pulse)
                print(trailing_pulse)
                if leading_pulse > 13300 and leading_pulse < 13700:
                    if trailing_pulse > 500 and trailing_pulse < 650:
                        # successfulTranslate is set to the value returned from
                        # the translateRawIRdata function
                        successfulTranslate = self.translateRawIRdata()

                        # if translateRawIRdata returns the rawBits list
                        if successfulTranslate:
                            # run the formattedBytes function to return the
                            # formatted string
                            formattedBytes = self.formattedBytes(
                                successfulTranslate)
                            print(formattedBytes)
                            yield(0)

                        # if translateRawIRdata returns False, re-evaluate the data
                        # and then break out of the while loop to start at the top
                        # and be retested. Repeat until a set of rawBits is found
                        else:
                            while not successfulTranslate:
                                successfulTranslate = self.translateRawIRdata()
                                break
                    else:
                        self.clearData()
                else:
                    print('here')
                    print(len(self.data))
                    start = False
                    for i in range(0, len(self.data) - 3, 2):
                        delta = self.data[i + 2] - self.data[i]
                        # adjust data if overflowed
                        if delta < 0:
                            delta = delta + 65535
                        print(delta)

                        if delta > 13300 and delta < 13700:
                            start = i
                            print('start' + str(start))
                            break

                    if start:
                        print('asd')
                        del self.data[0:i]
                    else:
                        print('12')
                        self.clearData()
            self.appendData()
            print('end' + str(len(self.data)))
