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
import ultrasonic
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

IR = infared.Infared(P.IR, C.IR_TIMER, C.IR_CH)

DRIVE = M.Drive(M1, M2, ENC1, ENC2, MC1, MC2)


run = task_share.Share('I', thread_protect=False, name="run")

turn = task_share.Share('I', thread_protect=False, name="turn")
turn.put(0)
turning = task_share.Share('I', thread_protect=False, name="turning")
turning.put(0)


def driveTask():

    FORWARD = const(1)
    REVERSE = const(2)
    TURN = const(3)
    STOP = const(4)

    state = STOP
    while True:
        if state == FORWARD:
            if IR.getCommand() == C.STOP:
                state = STOP
                yield(state)
            if turn.get():
                print(turn.get())
                state = REVERSE
                yield(state)
            DRIVE.forward(20)

        elif state == REVERSE:
            turning.put(1)
            if IR.getCommand() == C.STOP:
                state = STOP
                yield(state)
            if DRIVE.reverseBeforeTurn():
                state = TURN
                DRIVE.zeroEncoders()
                yield(state)

        elif state == TURN:
            if IR.getCommand() == C.STOP:
                state = STOP
                yield(state)
            turnState = turn.get()
            if DRIVE.turn(turnState):
                state = FORWARD
                DRIVE.zeroEncoders()
                turning.put(0)
                turn.put(0)
                yield(state)

        elif state == STOP:
            if IR.getCommand() == C.START:
                state = FORWARD
                yield (state)
            DRIVE.stop()

        yield (state)


def lineFollowerTask():
    LF = lineFollower.LineFollower(P.QRT_EN, P.QRT_ARRAY, 10)

    OFF = const(0)
    ANALYZE = const(1)

    state = OFF
    while True:
        if state == ANALYZE:
            if IR.getCommand() == C.STOP:
                state = OFF
                yield(state)
            sensorData = LF.analyzeSensorData()
            print(sensorData)
            if turning.get() == 0:
                turn.put(sensorData)
            yield(state)
        if state == OFF:
            if IR.getCommand() == C.START:
                state = ANALYZE
                yield (state)
        yield(state)


def ultraSonicDistanceTask():
    US = ultrasonic.Ultrasonic(P.US_DIST_TRIG, P.US_DIST_ECHO)

    OFF1 = const(0)
    ANALYZE1 = const(1)

    state = OFF1

    while True:
        if state == ANALYZE1:
            if IR.getCommand() == C.STOP:
                state = OFF1
                yield(state)
            distance = US.distance_in_inches()
            if distance > 1 and distance < 4:
                print('object detected')
            else:
                print('object not detected: ' + str(distance))
            yield(state)
        if state == OFF1:
            if IR.getCommand() == C.START:
                state = ANALYZE1
                yield(state)
        yield(state)


if __name__ == "__main__":

    try:
        print('\033[2JTesting scheduler in cotask.py\n')

        # intitialize motor task 1 using Task()
        t1 = cotask.Task(driveTask, name='Drive Task', priority=2,
                         period=10, profile=True, trace=False)

        t2 = cotask.Task(lineFollowerTask, name='Line Follower Task',
                         priority=2, period=50, profile=True, trace=False)
        t3 = cotask.Task(ultraSonicDistanceTask, name='UltraSonic Distance Task',
                         priority=3, period=50, profile=True, trace=False)
        # add each task to the task list
        cotask.task_list.append(t1)
        cotask.task_list.append(t2)
        cotask.task_list.append(t3)
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
