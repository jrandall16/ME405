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
ir_data_full = task_share.Share ('I', thread_protect = False, name = "Share_0")

# define a queue to be used as a buffer for interrupt timestamp data
ir_data = task_share.Queue ('I', 68, thread_protect = False, overwrite = False, name = "Queue_0")


## using a defined timer, collect the timestamp data from the IR signal.
def callback_fun (timer):
    # put the timestamp data into the queue when the share value is 0
    if ir_data.full() == 1:
        # if the queue is full, set the share value to 1
        ir_data_full.put(1, in_ISR=True)
    
    if ir_data_full.get(in_ISR=True) == 0:
        ir_data.put (timer.channel(1).capture(), in_ISR=True )


# assign pinA8 as an input pin to read the incoming data from the IR sensor
pinA8 = pyb.Pin (pyb.Pin.board.PA8, pyb.Pin.IN)

# set up the correct timer for pinA8. Assign the timer a 16-bit period and a prescaler of 79 to collect accurate timestamps
tim = pyb.Timer (1, prescaler=79, period=0xFFFF)

# set up the timer object to detect edges 
ch1 = tim.channel(1, pyb.Timer.IC, polarity = pyb.Timer.BOTH, pin = pinA8, callback = callback_fun)

if __name__ == "__main__":
    data = []
    subdata = []
    ir_data_full.put(0)
while True:
        if ir_data_full.get() == 1:
            while not ir_data.empty():
                data.append(ir_data.get())
            ir_data_full.put(0)

            # find the difference between edges 
            for i in range (len(data) - 1):

                delta = data[i+1] - data[i]
                
                if delta < 0:
                    delta = delta + 65535
                subdata.append(delta)
            leading_pulse = subdata[0] + subdata[1]
            print (leading_pulse)
            if leading_pulse > 13000 and leading_pulse < 15000:

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

                raw_bytes = '{:#010b}'.format(raw_bytes)
                address_byte_decimal = address_byte
                address_byte = '{:#010b}'.format(address_byte)
                naddress_byte = '{:#010b}'.format(naddress_byte)
                command_byte_decimal = command_byte
                command_byte = '{:#010b}'.format(command_byte)
                ncommand_byte = '{:#010b}'.format(ncommand_byte)

                print('--------------- New Packet ---------------\n'
                    + '  RAW:  ' + raw_bytes + '\n'
                    + ' ADDR:  ' + address_byte + '\n'
                    + 'nADDR:  ' + naddress_byte + '\n'
                    + '  CMD:  ' + command_byte + '\n'
                    + ' nCMD:  ' + ncommand_byte + '\n'
                    + '\n'
                    + 'Address (Decimal):  ' + str(address_byte_decimal) + '\n'
                    + 'Command (Decimal):  ' + str(command_byte_decimal) + '\n'
                    + '------------------------------------------')
                data = []
                subdata = []
            else:
                x = False
                for i in range (0,len(subdata) - 1,2):
                    total = subdata[i] + subdata[i+1]
                    if total > 13000 and total < 15000:
                        print('heres the leading pulse: ' + str(total))
                        x = i
                if x:
                    print (subdata)
                    del subdata[0:x]
                    del data[0:x+1]
                    print (subdata)
                else:
                    data = []
                    subdata = []
        else:
            pass