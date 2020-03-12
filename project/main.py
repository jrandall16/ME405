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
us_rear = task_share.Share('I', thread_protect=False, name="back approach")
us_rear.put(0)
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

    state = FORWARD
    # state = STOP
    while True:
        if state == FORWARD:
            # if IR.getCommand() != C.START:
            #     state = STOP
            #     yield(state)
            if turn.get() >= 1 and turn.get() <= 3:
                # print(turn.get())
                state = REVERSE
                turning.put(1)
                yield(state)
            elif turn.get() == 4:
                state = TURN
                turning.put(1)
                yield(state)
            DRIVE.forward(50)

        elif state == REVERSE:
            # if IR.getCommand() != C.START:
            #     state = STOP
            #     yield(state)
            if DRIVE.reverseBeforeTurn():
                state = TURN
                # DRIVE.zeroEncoders()
                yield(state)

        elif state == TURN:
            # if IR.getCommand() != C.START:
            #     state = STOP
            #     yield(state)
            turnState = turn.get()
            if DRIVE.turn(turnState): # will this let the bot turn?
                state = FORWARD
                # DRIVE.zeroEncoders()
                turning.put(0)
                turn.put(0)
                yield(state)

        elif state == STOP:
            # if IR.getCommand() == C.START:
            #     state = FORWARD
            #     yield (state)
            DRIVE.stop()

        yield (state)


def lineFollowerTask():
    LF = lineFollower.LineFollower(P.QRT_EN, P.QRT_ARRAY, 10)

    OFF = const(0)
    ANALYZE = const(1)

    state = ANALYZE
    while True:
        if state == ANALYZE:
            # if IR.getCommand() != C.START:
            #     state = OFF
            #     yield(state)
            sensorData = LF.analyzeSensorData()
            print(sensorData)
            if turning.get() == 0:
                turn.put(sensorData)
            yield(state)

        if state == OFF:
            # if IR.getCommand() == C.START:
            #     state = ANALYZE
            yield (state)

        yield(state)

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

    OFF1 = const(0) # pylint: disable=undefined-variable
    ANALYZE_US = const(1)
    ANALYZE_FRONT = const(2)
    ANALYZE_REAR = const(3)
    ANALYZE_RIGHT = const(4)
    ANALYZE_LEFT = const(5)
    ANALYZE_BOT = const(6)
    DONT_ANALYZE_US = const(7)

    state = ANALYZE_US

    def eStop(state):
        if IR.getCommand() != C.START:
            state = OFF1
        return state

    def checkForTurning(state):
        if turning.get() != 0:
            state = DONT_ANALYZE_US
        return state

    def checkSensor(state, direction, last_dir, last_prox):
        if direction == 'front':
            uSensor = US_2
            share = us_front
        elif direction == 'left':
            uSensor = US_4
            share = us_left
        elif direction == 'right':
            uSensor = US_3
            share = us_right
        elif direction == 'rear':
            uSensor = US_1
            share = us_rear

        distance = uSensor.distance_in_inches()  


        if distance < 12:
            # print('FORWARD TRIG')
            # print(distance_front)
            level = 1
            share.put(level)
            # us_front.put(4)
        # for a bot in approaching position from the front, turn 180 degress
        # and drive away
        elif distance > 12 and distance < 18:
            # print('FORWARD TRIG')
            # print(distance_front)
            level = 2
            share.put(level)
            # us_front.put(3)

        # for a bot in detected position from the front, turn 180 degrees 
        # and drive away
        elif distance > 18 and distance < 24:
            # print('FORWARD TRIG')
            # print(distance_front)
            level = 3
            share.put(level)

        # if safe ahead, drive there
        elif distance > 24 and distance < 30:
            # print('safe ahead')
            level = 4
            share.put(level)

        elif distance > 30:
            # print('no threat')
            # print(distance_front)
            level = 5
            share.put(level)
        
        print(str('us ') + direction + ': ' + str(share.get()))

        if share.get() != 5:
            curr_dir = state - 1
            curr_prox = share.get()
            if last_prox < curr_prox:
                curr_prox = last_prox
                curr_dir = last_dir
            else:
                pass
        else:
            curr_prox = last_prox
            curr_dir = last_dir

        last_prox = curr_prox
        last_dir = curr_dir
        # print(str('incoming from: ') + str(us_current_dir.get()))
        # print(str('proximity: ') + str(us_current_prox.get()))
        
        checkForTurning(state)

        state = state + 1
        return curr_dir, curr_prox, last_dir, last_prox, state

    while True:

        if state == ANALYZE_US:
            
            state = ANALYZE_FRONT
            last_prox = 5
            last_dir = 1
            # curr_dir = 1
            # curr_prox = 5

            state = checkForTurning(state)
            # state = eStop(state)  
            print(state)
            yield(state)

        if state == ANALYZE_FRONT:

            curr_dir, curr_prox, last_dir, last_prox, state = checkSensor(state,
                                                'front', last_dir, last_prox)
            state = checkForTurning(state)
            # state = eStop(state)  
            print(state)
            yield(state)

        if state == ANALYZE_REAR:
            # REAR US SENSOR
            # for a bot in closing position from the rear, turn 90 degrees and drive away
            curr_dir, curr_prox, last_dir, last_prox, state = checkSensor(state,
                                                'rear', last_dir, last_prox)
            state = checkForTurning(state)
            # state = eStop(state)            
            print(state)
            yield(state)

        if state == ANALYZE_RIGHT:
            ## RIGHT US SENSOR
            #for a bot in closing position from the right
           
            curr_dir, curr_prox, last_dir, last_prox, state = checkSensor(state,
                                                'right', last_dir, last_prox)
            state = checkForTurning(state)
            # state = eStop(state)            
            print(state)
            yield(state)

        if state == ANALYZE_LEFT:
            eStop(state)

            # ## LEFT US SENSOR
            # for a bot in closing position from the left
            curr_dir, curr_prox, last_dir, last_prox, state = checkSensor(state,
                                                'left', last_dir, last_prox)

            state = checkForTurning(state)
            # state = eStop(state)
            print(state)
            yield(state)

        if state == ANALYZE_BOT:
            print('analyze bot')

            print(curr_dir)
            print(curr_prox)
            us_current_dir.put(curr_dir)
            us_current_prox.put(curr_prox)

            if curr_prox == 1:
                if curr_dir == 1: # front
                    turn.put(2)
                elif curr_dir == 2: # back
                    turn.put(4)
                elif curr_dir == 3: # right
                    turn.put(1)
                elif curr_dir == 4: # left
                    turn.put(1)
                
            state = ANALYZE_US
            # state = eStop(state)
            print(state)
            yield(state)
            
        if state == DONT_ANALYZE_US:
            if turning.get == 0:
                state = ANALYZE_US
            
            # state = eStop(state)
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
                         priority=2, period=100, profile=True, trace=False)
           
        # add each task to the task list
        cotask.task_list.append(t1)
        # cotask.task_list.append(t2)
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
