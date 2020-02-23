import pyb
import infared

ir = infared.Infared(pyb.Pin.board.PA8, 1, 1)

ir.readInfaredSensorTask()
