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

us_front = task_share.Share('I', thread_protect=False, name="front approach")
us_front.put(0)
us_back = task_share.Share('I', thread_protect=False, name="back approach")
us_back.put(0)
us_left = task_share.Share('I', thread_protect=False, name="left approach")
us_left.put(0)
us_right = task_share.Share('I', thread_protect=False, name="right approach")
us_right.put(0)
us_last = task_share.Share('I', thread_protect=False, name="last approach")
us_last.put(0)
us_current_dir = task_share.Share('I', thread_protect=False, name="incoming bot side")
us_current_dir.put(0)
us_current_prox = task_share.Share('I', thread_protect=False, name="current proximity")
us_current_prox.put(0)

def driveTask():

    FORWARD = const(1)
    REVERSE = const(2)
    TURN = const(3)
    STOP = const(4)

    state = STOP
    while True:
        if state == FORWARD:
            if IR.getCommand() != C.START:
                state = STOP
                yield(state)
            if turn.get():
                # print(turn.get())
                state = REVERSE
                yield(state)
            DRIVE.forward(20)

        elif state == REVERSE:
            turning.put(1)
            if IR.getCommand() != C.START:
                state = STOP
                yield(state)
            if DRIVE.reverseBeforeTurn():
                state = TURN
                DRIVE.zeroEncoders()
                yield(state)

        elif state == TURN:
            if IR.getCommand() != C.START:
                state = STOP
                yield(state)
            turnState = turn.get()
            if DRIVE.turn(turnState): # will this let the bot turn?
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
            if IR.getCommand() != C.START:
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

def testTask():
    while True:
        print('test')
        yield(0)

def ultraSonicDistanceTask():
    '''Is a bot too close? Run away. Is a bot almost too close? Run away. Can
    you see the bot? Run away. Running away is our bots survival tactic. If an
    enemy bot is detected within a 2 foot square area, our bot will turn an
    appropriate direction and continue running. The sensors are checked
    in order, so the front and rear sensors must be checked first. The sensors
    are sensitive, if anything is detected further than 30 inches away it is 
    disregarded and the bot can run on.'''

    US_1 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_1, P.US_DIST_ECHO_1)
    US_2 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_2, P.US_DIST_ECHO_2)
    US_3 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_3, P.US_DIST_ECHO_3)
    US_4 = ultrasonic.Ultrasonic(P.US_DIST_TRIG_4, P.US_DIST_ECHO_4)

    OFF1 = const(0)
    ANALYZE_US = const(1)
    ANALYZE_FRONT = const(2)
    ANALYZE_BACK = const(3)
    ANALYZE_RIGHT = const(4)
    ANALYZE_LEFT = const(5)
    DONT_ANALYZE_US = const(6)

    state = ANALYZE_US

    while True:
        
        if state == ANALYZE_US:
            # if IR.getCommand() != C.START:
            #     state = OFF1
            #     yield(state)
            
            if turning.get() == 1:
                state = DONT_ANALYZE_US
                yield(state)
            
            state = ANALYZE_FRONT
            last_prox = 0
            last_dir = 0
            yield(state)

        if state == ANALYZE_FRONT:
            # if IR.getCommand() != C.START:
            #     state = OFF1
            #     yield(state)

            # 2 feet is a safe range of detection, so 2.5 feet is safer.
            # Set different share values for directions detected.

            distance_front = US_2.distance_in_inches()  
            ## FRONT US SENSOR
            # for a bot in closing position from the front, there is no time to 
            # turn the full 180 degrees. Turn 90 degrees and drive away
            if distance_front < 12:
                # print('FORWARD TRIG')
                # print(distance_front)
                us_front.put(4)
            # for a bot in approaching position from the front, turn 180 degress
            # and drive away
            elif distance_front > 12 and distance_front < 18:
                # print('FORWARD TRIG')
                # print(distance_front)
                us_front.put(3)

            # for a bot in detected position from the front, turn 180 degrees 
            # and drive away
            elif distance_front > 18 and distance_front < 24:
                # print('FORWARD TRIG')
                # print(distance_front)
                us_front.put(2)

            # if safe ahead, drive there
            elif distance_front > 24 and distance_front < 30:
                # print('safe ahead')
                us_front.put(1)

            elif distance_front > 30:
                # print('no threat')
                # print(distance_front)
                us_front.put(0)

            print(str('us_front: ') + str(us_front.get()))

            if us_front.get() != 0:
                curr_dir = ANALYZE_FRONT-1
                curr_prox = us_front.get()
                if last_prox > curr_prox
                    curr_prox = last_prox
                    curr_dir = last_dir
                else:
                    pass

            print(str('incoming from: ') + str(us_current_dir.get()))
            print(str('proximity: ') + str(us_current_prox.get()))
            
            state = ANALYZE_BACK
            yield(state)

        if state == ANALYZE_BACK:
            # if IR.getCommand() != C.START:
            #     state = OFF1
            #     yield(state)
            # REAR US SENSOR
            # for a bot in closing position from the rear, turn 90 degrees and drive away
            
            distance_back = US_1.distance_in_inches()    

            if distance_back < 12:
                # print('BEHIND TRIG')
                # print(distance_back)
                us_back.put(4)

            # for a bot in approaching position from the rear, turn 90 degress and drive away
            elif distance_back > 12 and distance_back < 18:
                # print('BEHIND TRIG')
                # print(distance_back)
                us_back.put(3)

            # for a bot in detected position from the rear, turn 90 degrees and drive away
            elif distance_back > 18 and distance_back < 24:
                # print('BEHIND TRIG')
                # print(distance_back)
                us_back.put(2)

            # if safe behind, drive there
            elif distance_back > 24 and distance_back < 30:
                # print('safe behind')
                us_back.put(1)

            # if out of 30 inch range, bot is safe
            elif distance_back > 30:
                # print('no threat')
                # print(distance_back)
                us_back.put(0)

            print(str('us_back: ') + str(us_back.get()))

             if us_front.get() != 0:
                last_dir = curr_dir
                last_prox = curr_prox
                curr_dir = ANALYZE_BACK-1
                curr_prox = us_front.get()
                if last_prox > curr_prox
                    curr_prox = last_prox
                    curr_dir = last_dir
                else:
                    pass
            
            print(str('incoming from: ') + str(us_current_dir.get()))
            print(str('proximity: ') + str(us_current_prox.get()))
            
            state = ANALYZE_RIGHT
            yield(state)

        if state == ANALYZE_RIGHT:
            # if IR.getCommand() != C.START:
            #     state = OFF1
            #     yield(state)
            ## RIGHT US SENSOR
            #for a bot in closing position from the right
           
            distance_right = US_3.distance_in_inches()

            if distance_right < 12:
                # print('RIGHT TRIG')
                # print(distance_right)
                us_right.put(34)

            # for a bot in approaching position from the front, turn 180 degress
            # and drive away
            elif distance_right > 12 and distance_right < 18:
                # print('RIGHT TRIG')
                # print(distance_right)
                us_right.put(33)

            # for a bot in detected position from the front, turn 180 degrees 
            # and drive away
            elif distance_right > 18 and distance_right < 24:
                # print('RIGHT TRIG')
                # print(distance_right)
                us_right.put(32)

            # if safe ahead, drive there
            elif distance_right > 24 and distance_right < 30:
                # print('space right')    
                # print(distance_right)
                us_right.put(31)
            
            elif distance_right > 30:
                # print('no threat')
                # print(distance_right)
                us_right.put(30)

            print(str('us_right: ') + str(us_right.get()))     

            if us_right.get() != 0:
                last_dir = curr_dir
                last_prox = curr_prox
                curr_dir = ANALYZE_RIGHT-1
                curr_prox = us_right.get()
            if last_prox > curr_prox
                    curr_prox = last_prox
                    curr_dir = last_dir
                else:
                    pass
            print(str('incoming from: ') + str(us_current_dir.get()))
            print(str('proximity: ') + str(us_current_prox.get()))


            
            state = ANALYZE_LEFT
            yield(state)

        if state == ANALYZE_LEFT:
            # if IR.getCommand() != C.START:
            #     state = OFF1
            #     yield(state)

            # ## LEFT US SENSOR
            # for a bot in closing position from the left
           
            distance_left = US_4.distance_in_inches()

            if distance_left < 12:
                # print('LEFT TRIG')
                # print(distance_left)
                us_left.put(44)

            # for a bot in approaching position from the left
            elif distance_left > 12 and distance_left < 18:
                # print('LEFT TRIG')
                # print(distance_left)
                us_left.put(43)

            # for a bot in detected position from the left, turn right and drive away
            elif distance_left > 18 and distance_left < 24:
                # print('LEFT TRIG')
                # print(distance_left)
                us_left.put(42)

            # if safe left, drive there
            elif distance_left > 24 and distance_left < 30:
                # print('space left')    
                us_left.put(41)

            elif distance_left > 30:
                # print('no threat')
                # print(distance_left)
                us_left.put(40)

            print(str('us_left: ') + str(us_left.get()))

            if us_left.get() != 0:
                last_dir = curr_dir
                last_prox = curr_prox
                curr_dir = ANALYZE_LEFT-1
                curr_prox = us_left.get()
            if last_prox > curr_prox
                    curr_prox = last_prox
                    curr_dir = last_dir
                else:
                    pass       

            print(str('incoming from: ') + str(us_current_dir.get()))
            print(str('proximity: ') + str(us_current_prox.get()))
            state = ANALYZE_BOT
            yield(state)

        if state == ANALYZE_BOT
            #if IR.getCommand() != C.START:
            #     state = OFF1
            #     yield(state)
            us_current_dir.put(curr_dir)
            us_current_prox.put(curr_prox)
            state = ANALYZE_FRONT
            yield(state)
            
        if state == DONT_ANALYZE_US:
            if turning.get == 1:
                state = DONT_ANALYZE_US
            if turning.get == 0:
                state = ANALYZE_US
            yield(state)

        if state == OFF1:
            if IR.getCommand() == C.START:
                state = ANALYZE_US
            yield(state)
        

if __name__ == "__main__":

    try:
        print('\033[2JTesting scheduler in cotask.py\n')

        # intitialize motor task 1 using Task()
        t1 = cotask.Task(driveTask, name='Drive Task', priority=1,
                         period=10, profile=True, trace=False)

        t2 = cotask.Task(lineFollowerTask, name='Line Follower Task',
                         priority=1, period=50, profile=True, trace=False)
        t3 = cotask.Task(ultraSonicDistanceTask, name='UltraSonic Distance Task',
                         priority=2, period=50, profile=True, trace=False)
        t4 = cotask.Task(testTask, name='Test Task',
                         priority=2, period=5, profile=True, trace=False)                 
        # add each task to the task list
        cotask.task_list.append(t1)
        cotask.task_list.append(t2)
        cotask.task_list.append(t3)
        cotask.task_list.append(t4)
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
