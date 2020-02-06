from matplotlib import pyplot
import serial_controller
import time

serial_port = serial_controller.Serial('/dev/cu.usbmodem205537A735412')
data = []
newdata = []
time_ms = []
position = []
t_end = time.time() + 6
try:
    serial_port.write('\x04')
    time.sleep(1)
    while time.time() < t_end:
        x = serial_port.read()
        data.append(x.decode().rstrip())
    # print(data[0])
    # print(data)
    time.sleep(0.5)
    serial_port.write('\x03')
    serial_port.close()
    
    for point in data:
        newdata.append(point.split(',',2))
    firstline = ['firstline']
    firstline = newdata.index(firstline)
    ticks_corrected = int(newdata[firstline + 1][1])
    
    for point in newdata:
        
        if newdata.index(point) > firstline:

            position.append(int(point[0]))
            time_ms.append(int(point[1]) - ticks_corrected)

        else:
            pass
    
    pyplot.plot(time_ms, position)
    pyplot.title('Position vs Time')
    pyplot.show ()


except KeyboardInterrupt:
    serial_port.write('\x03')
    serial_port.close()


    

