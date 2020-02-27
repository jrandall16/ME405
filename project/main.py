import pyb # pylint: disable=import-error
import utime # pylint: disable=import-error
import cotask
import task_share
import print_task
import busy_task

import pins as P
import constant as C
import motors as M

M1 = M.MotorDriver(P.M1DIR, P.M1PWM, C.MOT_PWM_TIMER, C.MOT1_PWM_CH, C.MOT_FREQ, True)

M2 = M.MotorDriver(P.M2DIR, P.M2PWM, C.MOT_PWM_TIMER, C.MOT2_PWM_CH, C.MOT_FREQ, False)

ENC1 = M.Encoder(P.ENC1A, C.ENC1A_CH, P.ENC1B, C.ENC1B_CH, C.ENC1_TIMER)

ENC2 = M.Encoder(P.ENC2A, C.ENC2A_CH, P.ENC2B, C.ENC2B_CH, C.ENC2_TIMER)
