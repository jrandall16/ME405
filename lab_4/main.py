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

## using the assigned timer, collect the timestamp data from the IR signal.
def callback_fun (timer):
    # put the timestamp data into the queue when the share value is 0
    while s0.get() == 0:
        q0.put (timer.counter(), in_ISR=True)

        # if the queue is full, set the share value to 1
        if q0.full():
            s0.put(1)

# assign pinA8 as an input pin to read the incoming data from the IR sensor
pinA8 = pyb.Pin (pyb.Pin.board.PA8, pyb.Pin.IN)

# set up the correct time for pinA8. Assign the timer a 16-bit period and a prescaler of 79 to collect accurate timestamps
tim = pyb.Timer (1, prescaler=79, period=0xFFFF)

# set up the timer object to detect edges using interrupt detection
ch1 = tim.channel(1, pyb.Timer.IC, polarity = pyb.Timer.BOTH, pin = pinA8)

callback = ch1.callback(callback_fun)

if __name__ == "__main__":

    data = []
    s0.put(0)
    while True:
        if s0.get() == 1:
            while not q0.empty():
                data.append(q0.get())
            s0.put(0)    

            #find the difference between edges 
            # newdata = []

            # for i in data:
            #     if data.index(i) > 1 and data.index(i) < 67:
            #     # if the index is a factor of two, find the difference of the two values and put it in a list
            #         if data.index(i)%2 != 0:
            #           newdata.append(data[data.index(i)] - data[data.index(i)-1]) 
        pass


            

