from micropython import const, alloc_emergency_exception_buf
import pyb
import utime
import cotask
import task_share
import print_task
import busy_task

# Allocate memory so that exceptions raised in interrupt service routines cangenerate useful diagnostic printouts
alloc_emergency_exception_buf (100)

s0 = task_share.Share ('I', thread_protect = False, name = "Share_0")

q0 = task_share.Queue ('I', 68, thread_protect = False, overwrite = False,
                    name = "Queue_0")

def callback_fun (timer):
    # print (timer.counter())
    while s0.get() == 0:
        q0.put (timer.counter(), in_ISR=True)
        if q0.full():
            s0.put(1)


pinA8 = pyb.Pin (pyb.Pin.board.PA8, pyb.Pin.IN)
tim = pyb.Timer (1, prescaler=79, period=0xFFFF)
ch1 = tim.channel(1, pyb.Timer.IC, polarity = pyb.Timer.BOTH, pin = pinA8)

callback = ch1.callback(callback_fun)

if __name__ == "__main__":

    s0.put(0)
    while True:
        if s0.get() == 1:
            while not q0.empty():
                print (q0.get())
            s0.put(0)       
        pass