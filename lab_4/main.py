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

    # if the queue is full, set the share value to 0 so the queue is not overwritten
    if q0.full():
        s0.put(1)
    # if the share value is 0, print the timestamp in the queue
    if s0.get() == 0:    
        q0.put (timer.channel(1).capture(), in_ISR=True )



# assign pinA8 as an input pin to read the incoming data from the IR sensor
pinA8 = pyb.Pin (pyb.Pin.board.PA8, pyb.Pin.IN)

# set up the correct timer for pinA8. Assign the timer a 16-bit period and a prescaler of 79 to collect accurate timestamps
tim = pyb.Timer (1, prescaler=79, period=0xFFFF)

# set up the timer object to detect edges 
ch1 = tim.channel(1, pyb.Timer.IC, polarity = pyb.Timer.BOTH, pin = pinA8, callback = callback_fun)


if __name__ == "__main__":

    # initialize an array to store the data in the queue
    data = []
    
    # initialize the share value to 0 so the queue is filled
    s0.put(0)

    while True:
        # if the queue is full, print the data in the queue
        if s0.get() == 1:
            while not q0.empty():
                data.append(q0.get())
            s0.put(0)



            # find the difference between edges in each section of the raw data
            subdata = []
            for i in range (len(data) - 1):

                delta = data[i+1] - data[i]
                
                if delta < 0:
                    delta = delta + 65535
                subdata.append(delta)
            
            if subdata[1] < 3000:
                print ('repeat code')

            # replace the data with the respective binary values
            raw = []
            for i in range (2,66,2):
                total = subdata[i] + subdata[i+1]
                # if the addition of two interrupt times is less than 1300, append a 0
                if total < 1300:
                    raw.append(0)
                # if the addition of two interrupt times is greater than 2000, append a 1
                elif total > 2000:
                    raw.append(1)
            # repeat for each section of the data and append 1's and 0's to the appropriate array        
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

            # intitialize a value to be updated
            raw_bytes = 0
            address_byte = 0
            naddress_byte = 0
            command_byte = 0
            ncommand_byte = 0

            # print each array backwards to create the correct 8-bit number
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
            
        pass


            

