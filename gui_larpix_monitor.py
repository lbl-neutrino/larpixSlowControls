####################################################################
# create a GUI to monitor the temperature and level of liquid in the
# larpix lab cryostat
####################################################################

import matplotlib.pyplot as plt
import tkinter as Tk
import tkinter.font 
import numpy as np

from numpy import arange, pi
from matplotlib.figure import Figure

# these functions are used to create a child window and checkbox
from tkinter import Toplevel, IntVar, Checkbutton

# this will be used to chose which temperature sensors to read
from tkinter import ttk

# FirgureCanvasTkAgg will place python figures in the GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# FuncAnimation continuously updates the time-serioes plots
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

# the "now" function in datetime formats dates and times
import datetime
import time

# the timezone() function will set the timezone in our clock
import pytz

# An SPI (Serial Peripheral Interface bus) transports information to or 
# from the AD7124-8
import spidev
spi = spidev.SpiDev()           # abreviate spidev

# format numbers on the plot axes
from matplotlib.ticker import FormatStrFormatter

####################################################################
# Functions
####################################################################

# display date and time in header of gui window
def clock():

    global new_run

    if new_run==0:
        first_date = datetime.datetime.now(pytz.timezone('US/Pacific'))
        first_date = first_date.strftime("%b %d, %Y %H:%M")
        new_run ==1

    nowd = datetime.datetime.now(pytz.timezone('US/Pacific'))
    nowd = nowd.strftime("%b %d, %Y %H:%M")
    root.title(f"Larpix Monitor     START: {first_date}   CURRENT: {nowd}")
    root.after(60_000, clock)	        # update date/time every 60s

# create buttons for quiting and chosing temperature sensors on the GUI
def buttons():

    buttonFont = Tk.font.Font(font="Helvetica", size=11, weight = 'bold')

    quit_button = Tk.Button(root, text="Quit Larpix Monitor", 
        bg='white', fg = 'blue', bd=4,
        relief = "raised",
        font = buttonFont,
        command=root.destroy)
    quit_button.grid(column=2, row=1)

    t_button = Tk.Button(root, text = "Select Temperature Sensors", 
        bg='white', fg = 'blue', bd=4,
        relief = "raised",
        font = buttonFont,
        command=lambda:add_sensors())
    t_button.grid(column=0, row=1)

# set up the mechanism used to communicate with the temperature ADC
def set_up_spi():
    bus = 0                         	# only SPI bus 0 is available
    device = 0                       	# chip select pin (0 or 1)
    spi.open(bus, device)           	# open the specified connection
    spi.max_speed_hz = 500000       	# set SPI speed
    # Mode 3 samples on falling edge, shifts out on rising edge
    spi.mode = 3 

# user can chose the temperature sensors of interest
def add_sensors():

    global sensors_live, sensor_1, sensor_2, sensor_3

    # function to call when checkbox is chosen
    def display_input():

        global sensors_live, sensor_1, sensor_2, sensor_3

        sensor_1 = var1.get()
        sensor_2 = var2.get()
        sensor_3 = var3.get()

        sensors_live = [1,1,sensor_1, sensor_2, sensor_3,1]

    # create a child window for sensor selection
    child = Toplevel(root)
    child.geometry("800x300")              # size of child window
    child.title("Temperature Sensor Selection")

    # show instructions
    child_label = Tk.Label(child, text="INSTRUCTIONS: \n\t- Temperatures" 
        " are always measured at bottom & top of the cryostat, "
        "& the bottom of the liquid container. \n\t- 3 sensors are "
        "available to place on the devices you are testing. Please choose"
        " at least one of them",
        bg = "white", bd = 4, justify='left', fg='blue', padx=10, pady=10,
        relief="ridge")
    child_label.grid(column=0, row=0, columnspan=3)

    # Define empty variables that will indicate checkbox selection 
    var1 = IntVar()
    var2 = IntVar()
    var3 = IntVar()

    ###############################################################
    # create three checkbuttons in 3 steps:
    #   - associate checkbutton with the empty variable, define on/off
    #     and give it a command if the variable is changed
    #   - store onvalue globally for the next time child window is called
    #   - place checkbutton on child window
    ###############################################################

    # checkbutton 1
    t1 = Checkbutton(child, text="Temperature Sensor 1", variable=var1,
         onvalue=1, offvalue=0, command=display_input, height=2)
    if sensor_1 == 1: t1.select()
    t1.grid(column=0, row=1)

    # checkbutton 2
    t2 = Checkbutton(child, text="Temperature Sensor 2", variable=var2,
         onvalue=1, offvalue=0, command=display_input, height=2)
    if sensor_2 == 1: t2.select()
    t2.grid(column=0, row=2)

    # checkbutton 3
    t3 = Checkbutton(child, text="Temperature Sensor 3", variable=var3,
         onvalue=1, offvalue=0, command=display_input, height=2)
    if sensor_3 == 1: t3.select()
    t3.grid(column=0, row=3)

    # create a button to close the child window
    buttonFont = Tk.font.Font(font="Helvetica", size=11, weight = 'bold')
    done_button = Tk.Button(child, text = "Done", 
        bg='white', fg = 'blue', bd=4,
        relief = "raised",
        font = buttonFont,
        command=lambda:child.destroy())                          
    done_button.grid(column=0, row=4, columnspan=3)

# read cdc a ten times. Take the median of every 5. Average the medians
def read_cdc():

    num_test = 10                           # number of cdc readings
    num_median = 5                          # size of the median set
    caps, median_levels = [], []
    cap, i, median_cap, level = 0,0,0,0

    # used to calibrate levels to capacitance
    sensor_length = 300
    min_cap = 1.0646713
    max_cap = 9.5106614

    while len(caps) < num_test:             # read capacitance from cdc
        val = bus.read_i2c_block_data(i2c_addr,0,19)
        if val[0] != 7:                     # val[0]=7 is old data
            cap = val[1]*2**16 + val[2]*2**8 + val[3]
            caps.append(cap)

    for i in range(0,len(caps),num_median):  # reduce noise using median

        # check to see if you have enough values left to get a median
        if len(caps[i:i+num_median]) < num_median:
            break                           # if not exit the function

        # measure median capacitance
        median_cap = np.median(caps[i:i+num_median])/1e6

        # transform capacitance into length
        median_level = (median_cap - min_cap) * sensor_length / (max_cap 
                        - min_cap)

        # add the new value to the list of median levels
        median_levels.append(median_level)

    # take the mean of median levels
    level = np.mean(median_levels)
    return level

# get a new temperature reading from the ADC
def read_adc():

    # initialize variables
    global t_start, new_ts
    write = 0
    read = 1            # command to read from ADC
    address_status = 0  # ADC status is available on register 0
    address_data = 2	# ADC Data is available on register 2
    address_ch0 = 9
    decimal_result = 0
    temperatures = [0,0,0,0,0,0]

    # 6 sensor register settings: enable, Ain positive, Ain negative
    sensor_inputs = [0b1100_0101,
                     0b0100_0001, 
                     0b0110_0010, 
                     0b1000_0011,
                     0b1010_0100, 
                     0b0010_0000]

    # used to calibrate ADC readings to degree C
    adc_910 =  10_118_174               # ADC reading for 920 Ohm
    adc_429 =   4_771_132               # ADC reading for 429 Ohm

    for sensor in range(0,6):

        # enable channel 0 to read the desired sensor's inputs
        msg = [address_ch0 + write*64, 0b1000_0000, sensor_inputs[sensor]]
        spi.xfer2(msg)

        # read the status register
        msg = [address_status + read*64, 0]
        status_result = spi.xfer2(msg)

        # keep reading the status register until there is new data 
        # (i.e. highest bit=0)
        while status_result[1] > 0b0111_111:
            status_result = spi.xfer2(msg)

        # read the new adc measurement
        msg = [address_data + read*64, 0, 0, 0]
        data_result = spi.xfer2(msg)

        # convert the 24 bit adc reading into a decimal value
        decimal_result = data_result[1]*(2**16) + data_result[2]*(2**8) + data_result[3]

        # Determine resistance for the sensor reading
        resistance = 91.02 + (42.94 - 91.02) * (decimal_result - adc_910) / (adc_429 - adc_910)

        # Convert resistance to temperature via interp function from
        # previously opened file convert_resistance_to_termperature.py,
        # First check range(19,390) which is necessary for the function
        if resistance < 19 or resistance > 390:
            if len(new_ts[sensor]) > 1:
                print(f"ADC reading {resistance} from sensor {sensor}"
                    " not in range(19,390) \nas required by "
                    "interp_resist_to_temp."
                    f"\nPrevious value {new_ts[sensor][-1]} will be "
                    "repeated.")
                temperatures[sensor] = new_ts[sensor][-1]

            else:
                print(f"The 1st ADC reading of {resistance} from sensor"
                    f" {sensor} not in range(19,390) \nas required by "
                    "interp_resist_to_temp.\n0 will be assigned")
                temperatures[sensor] = 0

        else:
            temperatures[sensor] = interp_resist_to_temp(resistance)

    return temperatures

# add a new reading to the 4 plots
def update_plots(frame):

    # initialize variables
    global t_start, sensors_live, file_name, t_labels_long, times
    global t_labels_short, set_number, new_ts, levels, new_data

    ##############################################################    
    # variables used for level meter graph. The colored arc is a 
    # stacked bar chart on a polar graph. It needs:
    #     xs: the angular center of each bar in radians
    #     widths: the size of each bar in radians
    #     colors: the color of each bar 
    ##############################################################
    
    p = np.pi                       # pi is needed to convert mm into radians
    low_l = 50                      # size of the lower level bar in mm
    low_l_x = p*(300-low_l)/300     # midpoint of lower level bar in radians
    green_width = 240-low_l         # size of green bar in radians
    green_x = 40 + green_width/2    # midpoint of green bar in radians
    yellow_x = 50 + green_width     # midpoint of yellow bar in radians
    red_x = 60 + green_width + low_l/2  # midpoint of upper red bar in radians
    widths = [p*20/300, p*20/300, p*(240-low_l)/300, p*20/300, p*low_l/300]
    xs     = [p*10/300, p*30/300, p*green_x/300, p*yellow_x/300, p*red_x/300]
    colors = ['r'      , "#FFD700" ,       "g", "#FFD700",       "r"]
    low_string = f"{low_l} mm"      # used to show size of the lower red bar

    ##############################################################
    # update level charts
    ##############################################################

    # get new time data
    times.append((time.time()-t_start)/60)

    # get new level data
    # The CDC is slow, which makes GUI button reactions slow. Updating
    # the root GUI before and after call to CDC solves this problem
    root.update()
    levels.append(read_cdc())        # read a new value from cdc
    root.update()

    # update the time-seris plot of level
    plotl.plot(times, levels, "b")

    # update the level meter plot
    ax1.cla()                               # erase the old meter
    ax1.bar(xs, width=widths, height=0.8, 	# arc of colored bars
            bottom=1.5, color=colors)

    # add black circle on the meter plot to display level value
    ax1.bar(p/2, width=2*p, height=0.7, bottom=0, color='k') 

    # add a needle on the meter plot indicating the current level
    level_angle = p*(300-levels[set_number])/300
    ax1.vlines(level_angle,.1, 2.3, color = 'k', lw=3)

    # print the level value at the center of the black circle
    level_string = f"{levels[set_number]:.0f} \nmm"
    ax1.annotate(level_string, xy=(0,0),
        horizontalalignment='center',
        verticalalignment='center', color='w', 
        size=11, fontweight='bold')

    # label the values of the lower and upper red regions
    ax1.annotate(low_string, xy=(low_l_x, 2.35),
        horizontalalignment='right',
        verticalalignment='center',
        color='r', 
        size=10)

    ax1.annotate('280 mm', xy=(p*20/300, 2.35),
        horizontalalignment='left',
        verticalalignment='center',
        color='r', 
        size=10)

    # display message stating ADC calibration conditions, which are
    # necessary to get a valid absolute value of the level readings
    ax1.annotate("Valid for 300mm sensor at T<-183C", xy=(p*1.5,1.5),
                 horizontalalignment='center', 
                 verticalalignment='center', 
                 color='k', 
                 size=11, fontweight='bold')

    # do not show the polar axes
    ax1.set_axis_off()

    ##############################################################
    # update temperature charts
    ##############################################################

    # initialize variables
    y1, y2 = [0,0,0,0,0,0],[0,0,0,0,0,0]
    t_colors = ['r','r','r','r','r','r']

    # clear the old temperature bar chart from the canvas
    ax2.cla()

    # get 6 new temperature values from adc
    new_data = read_adc()

    # cycle through all 6 channels
    for i in range(0,6):

        new_ts[i].append(new_data[i])

        # only plot sensors chosen by user for display
        if sensors_live[i] == 1:

            # update time series plot of chosen temperatures
            plott.plot(times, new_ts[i], label=t_labels_short[i], 
                       color=t_line_colors[i])

            # set bar heights and colors (y1, y2) for new temperature readings
            if new_ts[i][set_number] >= 0:
                y1[i]=new_ts[i][set_number]
                y2[i]=0
                t_colors[i] = 'r'
            elif new_ts[i][set_number] > -180: 
                t_colors[i] = 'powderblue'
                y1[i]=new_ts[i][set_number]
                y2[i]=0
            else: 
                t_colors[i] = 'powderblue'
                y1[i]=-180
                y2[i] = new_ts[i][set_number]+180

            # print current temperatures on bar chart
            t_label = f"{t_labels_long[i]}    {new_ts[i][set_number]:.2f}\xb0C"
            ax2.text(-175, i-.12, str(t_label), color='k', size=11)

        # for unchosen sensors, set its bar value to 0 with no label
        else:
            y1[i], y2[i] = 0,0

    # label and draw the -180C and 0C vertical lines on the bar chart
    ax2.text(-200, -1, "-180\xb0C", color='k', size=10)
    ax2.text(-10, -1, "0\xb0C", color='k', size=10)
    ax2.plot([-180, -180],[-0.5, 5.5], 'k--')
    ax2.plot([0, 0],[-0.5, 5.5], 'k-')

    # print all of the bars
    ax2.barh(t_labels_long, y1, color=t_colors)
    ax2.barh(t_labels_long, y2, left=y1, color='b')
    ax2.set_axis_off()
    ax2.set_xlim(-210,40)

    ##############################################################
    # print data to the file
    ##############################################################

    with open(file_name, "a") as file1:
        file1.write(f"{times[set_number]}\n")
        file1.write(f"{levels[set_number]}\n")
        for i in range(0,6):
            file1.write(f"{new_ts[i][set_number]}\n")

    set_number +=1

    # show all plots on the GUI
    plt.show()

####################################################################
# Open or create external files
####################################################################

# Start a data file to store history (file name will need start date)
start_date = time.strftime("%Y_%m_%d")
start_time = time.strftime("%H:%M")
file_name = "/data/larpix_history_" + start_date + ".txt"
with open(file_name, "w") as file1:
    file1.write(start_date + '\n')
    file1.write(start_time + '\n')

# open file that converts resistance to temperature
with open("convert_resistance_to_temperature.py") as convert_r:
    exec(convert_r.read())

# open file that initializes CDC registers to measure levels
with open("init_cdc.py") as init_l:
    exec(init_l.read())

# open file that initializes ADC registers to measure temperatures
with open("init_temperature_registers.py") as init_t:
    exec(init_t.read())

######################################################################
# set global variables
######################################################################

# start dates and times
new_run= 0
t_start = time.time()

# lists for plotted values
times = []
levels = []
new_ts = [[],[],[],[],[],[]]
new_data = []
set_number = 0

# used to keep track of which temperature sensors user chose to plot.
# The middle 3 may be chosen by user. The others are always plotted
sensors_live = [1,1,0,0,0,1]
sensor_1, sensor_2, sensor_3 = 0,0,0

# used for tempurature time-series plot
t_line_colors = ["forestgreen","silver","m","y","peru","greenyellow"]
t_labels_short = ["CrB","Bkt","S1","S2","S3","CrT"]
t_labels_long = ["Cryo Bottom","Bucket         ","Sensor 1      ",
                 "Sensor 2      ","Sensor 3      ","Cryo Top Plate"]

####################################################################
# Create the GUI interface and data file
####################################################################

# create a GUI (called root) and set its size
root = Tk.Tk()
root.geometry('800x600')

# create a figure on which to place 4 plots
fig = plt.Figure(figsize=(8,5.5))

# create a canvas for the figure and place it on the GUI
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=2, columnspan=3)

# a clock function displays START and LAST dates/times in GUI header
clock()

# create buttons for quiting the GUI and selecting temperature sensors
buttons()

####################################################################
# Create and place the level and temperature plots
####################################################################

# create level time-series plot
plotl = fig.add_subplot(221)                # place plot on upper left
plotl.set(title = "Level (mm)")
plotl.yaxis.set_major_formatter(FormatStrFormatter('% .0f'))
plotl.set_ylim(-10,310)

# get first set of data and initialize the level time-series plot
times.append((time.time()-t_start)/60)
levels.append(read_cdc())        # read a new value from cdc
plotl.plot(times, levels, "b")

# create level meter plot
ax1 = fig.add_subplot(223, polar = True)    # place plot on lower left
ax1.set_axis_off()

# create temperature bar chart
ax2 = fig.add_subplot(224)                   # place text on lower right
ax2.set_axis_off()                           # do not show axes
ax2.set_xlim(-210,40)

# create temperature time-series plot 
plott = fig.add_subplot(222)                # place plot on upper right
plott.set(title = "Temperature (C)")
plott.yaxis.set_major_formatter(FormatStrFormatter('% .0f'))
plott.set_ylim(-210,50)

# get 1st set of temperature readings & initialize the time-series plot
new_data = read_adc()
for i in reversed(range(0,6)):
    new_ts[i].append(new_data[i])
    plott.plot(times, new_ts[i], label=t_labels_short[i], 
               color=t_line_colors[i])

plott.legend(bbox_to_anchor=(1.2, 1), loc='upper right', fontsize="8")

# continuously update all plots using matplotlib's animation function
anil = animation.FuncAnimation(fig, update_plots, np.arange(1, 200), 
       interval=25, blit=False)

Tk.mainloop()

####################################################################
# Save the last frame of the animation
####################################################################

fig.savefig(f'./plots/larpix_plots_{start_date}')
print("\nFinal plots are available in the plots folder"
      "\nData is available in the data folder"
      "\nADC register settings are listed in the data file")

with open(file_name, "a") as file1:
    file1.write("end")
