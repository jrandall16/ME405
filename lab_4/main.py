import pyb # pylint: disable=import-error
import infared

ir = infared.Infared(pyb.Pin.board.PA8, 1, 1)

ir.readInfaredSensorTask()
