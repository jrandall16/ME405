import pyb  # pylint: disable=import-error
import utime  # pylint: disable=import-error
import cotask
import task_share
import print_task
import busy_task

import pins as P
import constant as C
import motors as M
import lineFollower
import infared
import gc

# comment these out after deploying code
M1 = M.MotorDriver(P.M1DIR, P.M1PWM, C.MOT_PWM_TIMER,
                   C.MOT1_PWM_CH, C.MOT_FREQ, True)
M2 = M.MotorDriver(P.M2DIR, P.M2PWM, C.MOT_PWM_TIMER,
                   C.MOT2_PWM_CH, C.MOT_FREQ, False)
MC1 = M.MotorController()
MC2 = M.MotorController()
ENC1 = M.Encoder(P.ENC1A, C.ENC1A_CH,
                 P.ENC1B, C.ENC1B_CH, C.ENC1_TIMER, True)
ENC2 = M.Encoder(P.ENC2A, C.ENC2A_CH,
                 P.ENC2B, C.ENC2B_CH, C.ENC2_TIMER)
DRIVE = M.Drive(M1, M2, ENC1, ENC2, MC1, MC2)


run = task_share.Share('I', thread_protect=False, name="run")

turn = task_share.Share('I', thread_protect=False, name="turn")
turning = task_share.Share('I', thread_protect=False, name="turning")
turning.put(0)


def driveTask():
    M1 = M.MotorDriver(P.M1DIR, P.M1PWM, C.MOT_PWM_TIMER,
                       C.MOT1_PWM_CH, C.MOT_FREQ, True)
    M2 = M.MotorDriver(P.M2DIR, P.M2PWM, C.MOT_PWM_TIMER,
                       C.MOT2_PWM_CH, C.MOT_FREQ, False)
    MC1 = M.MotorController()
    MC2 = M.MotorController()
    ENC1 = M.Encoder(P.ENC1A, C.ENC1A_CH,
                     P.ENC1B, C.ENC1B_CH, C.ENC1_TIMER, True)
    ENC2 = M.Encoder(P.ENC2A, C.ENC2A_CH,
                     P.ENC2B, C.ENC2B_CH, C.ENC2_TIMER)
    DRIVE = M.Drive(M1, M2, ENC1, ENC2, MC1, MC2)

    FORWARD = const(1)
    REVERSE = const(2)
    TURN = const(3)
    STOP = const(4)

    state = FORWARD
    while True:

        if state == FORWARD:
            if turn.get():
                print(turn.get())
                state = REVERSE
                yield(state)
            DRIVE.forward(20)

        elif state == REVERSE:
            turning.put(1)
            if DRIVE.reverseBeforeTurn():
                state = TURN
                DRIVE.zeroEncoders()
                yield(state)

        elif state == TURN:
            turnState = turn.get()
            if DRIVE.turn(turnState):
                state = FORWARD
                DRIVE.zeroEncoders()
                turning.put(0)
                turn.put(0)
                yield(state)

        elif state == STOP:
            DRIVE.forward(0)

        yield (state)


def lineFollowerTask():
    LF = lineFollower.LineFollower(P.QRT_EN, P.QRT_ARRAY, 10)

    OFF = const(0)
    ANALYZE = const(1)

    state = ANALYZE
    while True:
        if state == ANALYZE:
            sensorData = LF.analyzeSensorData()
            if turning.get() == 0:
                turn.put(sensorData)
        yield(state)


def InfaredRecieverTask():

    WAIT = const(0)
    TRANSLATE = const(1)
    # # Initialization for this task.
    # IR = infared.Infared(P.IR, C.IR_TIMER, C.IR_CH)

    # Data is a class scoped list that is filled with timestamps
    # from the ir_data queue
    IR.clearData()

    # run consistently (will have to yield for other tasks)
    state = WAIT
    run.put(0)
    while True:
        print('here')
        yield(state)
        # if state == WAIT:
        #     while len(IR.data) < 68:
        #         # append timestamps to the data list until it has 68
        #         # timestamps
        #         IR.appendData()
        #         state = WAIT
        #         yield (state)
        #     state = TRANSLATE
        #     yield (state)
        # if state == TRANSLATE:
        #     # successfulTranslate is set to the value returned from
        #     # the translateRawIRdata function
        #     successfulTranslate = IR.translateRawIRdata()

        #     # if translateRawIRdata returns the rawBits list
        #     if type(successfulTranslate) == list:
        #         # run the formattedBytes function to return the
        #         # formatted string
        #         formattedBytes = IR.formattedBytes(successfulTranslate)
        #         print(formattedBytes)
        #         run.put(1)
        #         state = WAIT
        #         yield(state)

        #     # if translateRawIRdata returns 1 (repeat code)
        #     elif successfulTranslate == 1:
        #         # print the last recieved formatted string
        #         print(formattedBytes)
        #         run.put(1)
        #         state = WAIT
        #         yield(state)
        #     # if translateRawIRdata returns False, re-evaluate the data
        #     # and then break out of the while loop to start at the top
        #     # and be retested. Repeat until a set of rawBits is found
        #     while not successfulTranslate:
        #         successfulTranslate = IR.translateRawIRdata()
        #         state = WAIT
        #         yield(state)


if __name__ == "__main__":

    try:
        print('\033[2JTesting scheduler in cotask.py\n')

        # intitialize motor task 1 using Task()
        t1 = cotask.Task(driveTask, name='Drive Task', priority=1,
                         period=5, profile=True, trace=False)

        t2 = cotask.Task(lineFollowerTask, name='Line Follower Task',
                         priority=1, period=100, profile=True, trace=False)
        t3 = cotask.Task(InfaredRecieverTask, name='Infared Reciever Task',
                         priority=2, profile=True, trace=False)

        IR = infared.Infared(P.IR, C.IR_TIMER, C.IR_CH)
        # add each task to the task list
        # cotask.task_list.append(t1)
        # cotask.task_list.append(t2)
        # cotask.task_list.append(t3)
        cotask.task_list.append(IR.task)

        # execute the task list using the priority attribute of each task

        while True:
            cotask.task_list.pri_sched()

        # Run the memory garbage collector to ensure memory is as defragmented as possible before the real-time scheduler is started
        gc.collect()

    # If a keyboard interrupt is thrown, set the motor duty cycles to 0
    except KeyboardInterrupt:
        DRIVE.stop()
    except Exception as e:
        print(e)
        DRIVE.stop()
