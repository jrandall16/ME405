from micropython import const, alloc_emergency_exception_buf
import pyb
import utime
import cotask
import task_share
import print_task
import busy_task

# Allocate memory so that exceptions raised in interrupt service routines cangenerate useful diagnostic printouts
alloc_emergency_exception_buf (100)

# define a share to be used as a flag to indicate when to read the queue of timestamp data
s0 = task_share.Share ('I', thread_protect = False, name = "Share_0")

# define a queue to be used as a buffer for interrupt timestamp data
q0 = task_share.Queue ('I', 68, thread_protect = False, overwrite = False, name = "Queue_0")


## using a defined timer, collect the timestamp data from the IR signal.
def callback_fun (timer):
    # put the timestamp data into the queue when the share value is 0
    if q0.full():
        s0.put(1)
    
    if s0.get() == 0:
        q0.put (timer.channel(1).capture(), in_ISR=True )
        # if the queue is full, set the share value to 1


# assign pinA8 as an input pin to read the incoming data from the IR sensor
pinA8 = pyb.Pin (pyb.Pin.board.PA8, pyb.Pin.IN)

# set up the correct timer for pinA8. Assign the timer a 16-bit period and a prescaler of 79 to collect accurate timestamps
tim = pyb.Timer (1, prescaler=79, period=0xFFFF)

# set up the timer object to detect edges 
ch1 = tim.channel(1, pyb.Timer.IC, polarity = pyb.Timer.BOTH, pin = pinA8, callback = callback_fun)

# I put the callback into the timer.channel object, should not make a difference. 
#callback = ch1.callback(callback_fun)

if __name__ == "__main__":

    data = []
    s0.put(0)
    while True:
        if s0.get() == 1:
            while not q0.empty():
                data.append(q0.get())
            s0.put(0)



            # find the difference between edges 
            subdata = []
            for i in range (len(data) - 1):

                delta = data[i+1] - data[i]
                
                if delta < 0:
                    delta = delta + 65535
                subdata.append(delta)
            
            if subdata[1] < 3000:
                print ('repeat code')

            raw = []
            for i in range (2,66,2):
                total = subdata[i] + subdata[i+1]
                if total < 1300:
                    raw.append(0)
                elif total > 2000:
                    raw.append(1)
            address = []
            for i in range (2,18,2):
                total = subdata[i] + subdata[i+1]
                if total < 1300:
                    address.append(0)
                elif total > 2000:
                    address.append(1)
            naddress = []
            for i in range (18,34,2):
                total = subdata[i] + subdata[i+1]
                if total < 1300:
                    naddress.append(0)
                elif total > 2000:
                    naddress.append(1)
            command = []
            for i in range (34,50,2):
                total = subdata[i] + subdata[i+1]
                if total < 1300:
                    command.append(0)
                elif total > 2000:
                    command.append(1)
            ncommand = []
            for i in range (50,66,2):
                total = subdata[i] + subdata[i+1]
                if total < 1300:
                    ncommand.append(0)

                elif total > 2000:
                    ncommand.append(1)


            raw_bytes = 0
            address_byte = 0
            naddress_byte = 0
            command_byte = 0
            ncommand_byte = 0

            for n in range (len(raw)):
                raw_bytes |= raw[n] << n
            for n in range (len(address)):
                address_byte |= address[n] << n
            for n in range (len(naddress)):
                naddress_byte |= naddress[n] << n
            for n in range (len(command)):
                command_byte |= command[n] << n
            for n in range (len(ncommand)):
                ncommand_byte |= ncommand[n] << n

            print('{:#010b}'.format(raw_bytes))
            print('{:#010b}'.format(address_byte))
            print('{:#010b}'.format(naddress_byte))
            print('{:#010b}'.format(command_byte))
            print('{:#010b}'.format(ncommand_byte))

                # if data.index(i) > 1 and data.index(i) < 67:
                # # if the index is a factor of two, find the difference of the two values and put it in a list
                #     if data.index(i)%2 != 0:
                #       subdata.append(int(data[data.index(i)] - data[data.index(i)-1]))
        #     # equate the differences to a 4 byte binary number    
        #     isrdata = []

        #     # find a value that splits all values in newdata. The low values represent 0's and the high values represent 1's
        #     midvalue = 0
        #     for i in subdata:
        #         if i < midvalue:
        #             isrdata.append(0)
        #         if i > midvalue:
        #             isrdata.append(1)

        #     # the data in isrdata is written in reverse binary with the least signifigcant bit in the most signifigcant bit spot
        #     # shift each value read from isrdata to the left to generate the appropriate binary data

        #     # initialize j as the indexes of isrdata
        #     j = len(isrdata)-1

        #     # initialize an array with the appropriate number of values to be filled in
        #     bindata = [None]*len(isrdata)

        #     # fill in each value for j greater than or equal to zero
        #     while j >= 0:
        #         # place each value in isrdata at the correct point in the array
        #         for i in isrdata:
        #             bindata[j] = i
        #             # decrement the index to fill in the array backwards.
        #             j = j-1
            
        pass


            

