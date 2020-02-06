from matplotlib import pyplot

x_values = []
y_values = []

global x_label
global y_label

with open("eric.csv") as myfile:
    lines = myfile.readlines()
    x_label = str(lines[1].split(", ")[0])
    y_label = str(lines[1].split(", ")[1])
    count = 0
    for line in lines:
        line_list = line.split(",",2)
        try:
            x_value = line_list[0].split('#')
            y_value = line_list[1].split('#')
            x_value = x_value[0]
            y_value = y_value[0]
            x_value = float(x_value)
            y_value = float(y_value)
            x_values.append(x_value)
            y_values.append(y_value)
            count += 1
        except:
            pass

pyplot.plot(x_values, y_values)
pyplot.title('Height vs Time')
pyplot.xlabel(x_label)
pyplot.ylabel(y_label)
pyplot.show ()