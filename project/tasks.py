# Initialize share variables that will be used in different tasks

## emergency is a transition variable that indicates the motor needs to stop
self.emergency = task_share.Share ('I', thread_protect = False, name = "emergency stop")

## turn is a transition variable that indicates the bot needs to turn
self.turn = task_share.Share ('I', thread_protect = False, name = "turn command")

## Kp is the proportional gain for the proportional only controller
self.Kp = task_share.Share ('I', thread_protect = False, name = "Kp")

## desiredSpeed is the speed the controller is trying to reach
self.desiredSpeed = task_share.Share ('I', thread_protect = False, name = "desired speed")

## currentSpeed is the current speed read from the encoder
self.currentSpeed = task_share.Share ('I', thread_protect = False, name = "current speed")

## level is the magnitude of ouptput DC voltage to the motor
self.level = task_share.Share ('I', thread_protect = False, name = "DC level")

## direction is the sign of the output voltage, causing the motor to spin a specified direction
self.direction = task_share.Share ('I', thread_protect = False, name = "drive direction")



## variable indicating a turn clockwise 90 degrees
self.cw90deg = task_share.Share ('I', thread_protect = False, name = "90 degree turn")

## variable indicating a turn clockwise 180 degrees
self. cw180deg = task_share.Share ('I', thread_protect = False, name = "180 degree turn")

## variable indicating a turn clockwise 360 degrees
self. cw360deg = task_share.Share ('I', thread_protect = False, name = "360 degree turn")

## variable indicating a turn counter-clockwise 90 degrees
self.ccw90deg = task_share.Share ('I', thread_protect = False, name = "90 degree turn")

## variable indicating a turn counter-clockwise 180 degrees
self. ccw180deg = task_share.Share ('I', thread_protect = False, name = "180 degree turn")

## variable indicating a turn counter-clockwise 360 degrees
self. ccw360deg = task_share.Share ('I', thread_protect = False, name = "360 degree turn")


###---------------------------------------------------------------------------------------###


## Define a task to drive motor_1
def motor_1_driver ():
    ''' This task drives motor_1 using input parameters level and direction. This task has 2 states. 
    State 1 runs the motor
    State 2 runs the motor to turn the bot a set amount of degrees
    Stae 3 stops the motor
    '''
    RUN = CONST(1)
    TURN = CONST(2)
    STOP = CONST(3)
    
    # call class MotorDriver() and initialize it with the required parameters
    motor = motors.MotorDriver(directionPin, PWMpin, PWMtimer, PWMchannel, freq)

    while True:
        if state = RUN:
            # if emergency, transition to STOP state
            if self.emergency:
                motor.set_duty_cycle(0,0)
                state = STOP
            # if turn, transition to TURN state
            elif self.turn:
                state = TURN
            # if none, 
            elif:
                motor.set_duty_cycle(self.level, self.direction)
                state = RUN
            yield(state)

        if state = TURN:
            if cw90deg:
                motor.set_duty_cycle(10,0)
            elif cw180deg:
                motor.set_duty_cycle(100,0)
            elif cw360deg:
                motor.set_duty_cycle(1000,0)
            elif ccw90deg:
                motor.set_duty_cycle(10,-0)
            elif ccw90deg:
                motor.set_duty_cycle(100,-0)
            elif ccw90deg:
                motor.set_duty_cycle(1000,-0)
            
            # always transition to RUN state
            state = RUN
            yield(state)

        if state = STOP:
            # if emergency is cleared, return to RUN state
            if not self.emergency:
                state = RUN
            # if emergency is not cleared, remain in STOP state and set PWM signal to 0.
            elif:
                motor.set_duty_cycle(0,0)
                state = STOP
            yield(state)

## Define a task to control motor_1
def motor_1_controller ():
    ''' This task controls motor_1 using input parameters Kp, desiredSpeed, and currentSpeed. This task has 2 states.
    State 1 runs the controller with the current input parameters
    State 2 runs the controller witht the necessary input parameters to turn the bot 
    State 3 stops the motor if emergency
    '''
    RUN = CONST(1)
    TURN = CONST(2)
    STOP = CONST(3)

    ## call class Controller()
    controller = motors.Controller(self.Kp, self.desiredSpeed)
    
    while True:
        if state = RUN:
            # if emergency, transition to STOP state
            if self.emergency:
                state = STOP
            # if turn, transition to TURN state
            elif self.turn:
                state = TURN
            # if none, continue in RUN state with the input values
            elif:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)
                state = RUN

            yield(state)

        # make a turn specified by the shares
        if state = TURN:
            if cw90deg:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)
            elif cw180deg:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)
            elif cw360deg:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)
            elif ccw90deg:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)
            elif ccw90deg:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)
            elif ccw90deg:
                controller.outputSpeed(self.currentSpeed)
                controller.setKp(self.Kp)
                controller.setDesiredSpeed(self.desiredSpeed)

            # always transition to RUN state
            state = RUN
            yield(state)

        if state = STOP:
            # if emergency is cleared, transition to RUN state
            if not self.emergency:
                state = RUN

            # if emergency is not cleared, set desiredSpeed to 0 and remain in STOP state
            elif:
                controller.setDesiredSpeed(0)
                state = STOP
            yield(state)

## Define a task to read the encoder on motor_1
def motor_1_encoder():
    ''' This task runs the motor_1 encoder using no input parameters encoderpinA, channelA, encoderpinB, channelB, and timer. This task has 1 states.
    State 1: This state reads the encoder and outputs the current speed
    State 2: This state resets the encoder to zero
    '''
    READ = CONST(1)
    RESET = CONST(2)

    ## call class Encoder()
    encoder = motors.Encoder (encoderpinA, channelA, encoderpinB, channelB, timer)

    while True:
        if state = READ:
            if emergency:
                state = RESET
            elif:
                encoder.read()
                state = READ
        if state = RESET:
            if not emergency:
                state = READ
                encoder.zero()
            elif:
                state = RESET