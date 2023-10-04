####################################################################
# create a GUI to monitor the temperature and level of liquid in the
# larpix lab cryostat
####################################################################

import matplotlib.pyplot as plt
import tkinter as Tk
import numpy as np
import tkinter.font 

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

# used to call the latest data file
import os

####################################################################
# Functions
####################################################################

# create buttons for quiting and chosing temperature sensors on the GUI
def buttons():

    buttonFont = Tk.font.Font(font="Helvetica", size=11, weight = 'bold')

    quit_button = Tk.Button(root, text="Quit Remote Larpix Monitor", 
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
    
# let user chose the termperature sensors they want to read
def add_sensors():

    global sensors_live, sensor_1, sensor_2, sensor_3

    # Define function to call when checkbox is chosen
    def display_input():

        global sensors_live, sensor_1, sensor_2, sensor_3
        write = 0                               # command to write to ADC

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
        "& the bottom of the liquid container. \n\t- 3 additional "
        "temperature sensors are available to place in other areas "
        "of interest, such as on the top of a device being tested.",
        bg = "white", bd = 4, justify='left', fg='blue', padx=10, pady=10,
        relief="ridge")
    child_label.grid(column=0, row=0, columnspan=3)

    # Define empty variables that will indicate checkbox selection 
    var1 = IntVar()
    var2 = IntVar()
    var3 = IntVar()

    # create three checkboxes and place them on the child grid
    t1 = Checkbutton(child, text="Temperature Sensor 1", variable=var1,
         onvalue=1, offvalue=0, command=display_input, height=2)
    if sensor_1 == 1: t1.select()
    t1.grid(column=0, row=1)

    t2 = Checkbutton(child, text="Temperature Sensor 2", variable=var2,
         onvalue=1, offvalue=0, command=display_input, height=2)
    if sensor_2 == 1: t2.select()
    t2.grid(column=0, row=2)

    t3 = Checkbutton(child, text="Temperature Sensor 3", variable=var3,
         onvalue=1, offvalue=0, command=display_input, height=2)
    if sensor_3 == 1: t3.select()
    t3.grid(column=0, row=3)

    # a button to close the child window
    buttonFont = Tk.font.Font(font="Helvetica", size=11, weight = 'bold')
    done_button = Tk.Button(child, text = "Done", 
        bg='white', fg = 'blue', bd=4,
        relief = "raised",
        font = buttonFont,
        command=lambda:child.destroy())                          
    done_button.grid(column=0, row=4, columnspan=3)

# add a new level and temperature readings to the 4 plots
def update_plots(frame):

    global sensors_live, num_lines, file_line, content, anil
    global num_full_sets, new_ts, times, levels, t_labels_short
    global t_labels_long

    stop_animation = False
    
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

    #################################################################
    # read a new set of level/temperature data from the data file
    # testing for 9 pieces of information instead of 8 is necessary
    # in case the last piece of information is "end"
    #################################################################

    while (num_lines - file_line) < 9:

        with open(file_name, "r") as file1:
            content = file1.readlines()
            num_lines = len(content)

            # this loop can be slow, making the buttons slow to react
            # Updating the root inside this loop solves the problem
            root.update()

            # If "end" of the lab run is reached stop the animation
            if (content[-1] == "end"):

                # let remote user know the run is over on terminal 
                print("\n\nThis run has been stopped in the lab. "
                      "\nFinal plots are available in the plots folder. "
                      "\nPlease close the monitor when you're done.")

                stop_animation = True
                break

    if stop_animation == False:
        num_full_sets +=1
        # read time and level from the content of the data file
        times.append(float(content[file_line-1]))
        file_line+=1

        levels.append(float(content[file_line-1]))
        file_line+=1

        # read 6 temperatures from the content of the data file
        for j in range(0,6):
            new_ts[j].append(float(content[file_line-1]))
            file_line+=1

    ##############################################################
    # update time series charts
    ##############################################################

    # update the level time-seris plot
    plotl.plot(times, levels, "b")

    level_string = str(int(levels[-1]))

    # update the level meter plot
    ax1.cla()                               # erase the old meter
    ax1.bar(xs, width=widths, height=0.8, 	# arc of colored bars
           bottom=1.5, color=colors)

    # add black circle on the meter plot to display level value
    ax1.bar(p/2, width=2*p, height=0.7, bottom=0, color='k') 

    # add a needle on the meter plot indicating the current level
    level_angle = p*(300-levels[-1])/300     # angle of needle
    ax1.vlines(level_angle,.1, 2.3, color = 'k', lw=3)

    # print the level value at the center of the black circle
    level_string = f"{levels[-1]:.0f} \nmm"  # format the text
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

    # print the calibration conditions for a valid reading
    ax1.annotate("Valid for 300mm sensor at T<-183C", xy=(p*1.5,1.5),
        horizontalalignment='center', verticalalignment='center', color='k', 
        size=11, fontweight='bold')

    # don't display the polar axes
    ax1.set_axis_off()

    ##############################################################
    # update temperature charts
    ##############################################################

    # used for temperature bar chart
    y1, y2 = [0,0,0,0,0,0],[0,0,0,0,0,0]
    t_bar_colors = ['r','r','r','r','r','r']

    # clear the old temperature bar chart
    ax2.cla()

    # cycle through all 6 channels
    for i in range(0,6):

        # only plot the sensors chosen by user
        if sensors_live[i] == 1:

            # update time-series plot of chosen temperatures
            plott.plot(times, new_ts[i], label=t_labels_short[i],
                       color=t_line_colors[i])
            # set bar heights and colors (y1, y2) for new temperature readings
            if new_ts[i][-1] >= 0:
                y1[i]=new_ts[i][-1]
                y2[i]=0
                t_bar_colors[i] = 'r'
            elif new_ts[i][-1] > -180: 
                t_bar_colors[i] = 'powderblue'
                y1[i]=new_ts[i][-1]
                y2[i]=0
            else: 
                t_bar_colors[i] = 'powderblue'
                y1[i]=-180
                y2[i] = new_ts[i][-1]+180

            # print current temperatures on bar chart
            t_label = f"{t_labels_long[i]}    {new_ts[i][-1]:.2f}\xb0C"
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
    ax2.barh(t_labels_long, y1, color=t_bar_colors)
    ax2.barh(t_labels_long, y2, left=y1, color='b')
    ax2.set_axis_off()
    ax2.set_xlim(-210,40)

    # if "end" was reached in data file, print information on GUI 
    if stop_animation:
        ax1.annotate("Lab run has finished", xy=(p*1.5,2.3),
                  horizontalalignment='center', 
                  verticalalignment='center', color='r', 
                  size=20, fontweight='bold')

    # show all plots on the GUI
    plt.show()
    
    # if data taking has stopped in the lab, stop the animation
    if stop_animation: anil.event_source.stop()

########################################################################
#                                                                      #
#                           MAIN                                       #
#                                                                      #
########################################################################

##############################################################
# open the data file
##############################################################

# ask user to chose which file to read
file_date = input("\nTo view the latest run enter y (otherise enter n):")

# View the latest file
if file_date =='y':

    directory_path = '/var/nfs/instrumentation_data/'
    most_recent_file = None
    most_recent_time = 0

# find the last file updated in directory_path
    for entry in os.scandir(directory_path):
        if entry.is_file():
            # get the modification time of the file using entry.stat().st_mtime_ns
            mod_time = entry.stat().st_mtime_ns
            if mod_time > most_recent_time:
                # update the most recent file and its modification time
                most_recent_file = entry.name
                most_recent_time = mod_time

    file_name = f"/var/nfs/instrumentation_data/{most_recent_file}"

    print(f"\nYou are reading data from: {file_name}\n")

    # if monitoring on-going lab run, start with the mandatory sensors
    # The user can add optional sensor via the sensor button
    sensors_live = [1,1,0,0,0,1]
    sensor_1, sensor_2, sensor_3 = 0,0,0

# view the results of previous lab runs
else: 

    # ask user to specify the date of interest
    file_date = input("Enter the date on the data file using"
                    "format: yyyy_mm_dd  ")
    file_name = f"/var/nfs/instrumentation_data/larpix_history_{file_date}.txt"

    # when reading a previous lab run, plot all temperature sensors
    sensors_live = [1,1,1,1,1,1]
    sensor_1, sensor_2, sensor_3 = 1,1,1

# open file. Count # of lines
with open(file_name, "r") as file1:
        content = file1.readlines()
        num_lines = len(content)

# check to make sure a full reading was writen to the file. Why 70?
#   - 61 lines are start date, start time, & ADC register settings 
#   - last line could be "end" if run has stopped
#   - 8 more lines would compose one full set of data
if num_lines < 70:
    print("No full reading has yet been stored in this file. Please "
            "try again later.")
    root.destroy
else:
    start_date = content[0]
    start_time = content[1]
    # lines 3-61 are the settings of the temperature ADC registers
    file_line = 62
    # don't count a potential "end" line as part of a data set
    num_full_sets = int((num_lines-file_line-1)/8)

######################################################################
# set global variables
######################################################################
new_run = 0

# initialize data lists and associated plot variables
times = []
levels = []
new_ts = [[],[],[],[],[],[]]
t_line_colors = ["forestgreen","silver","m","y","peru","greenyellow"]
t_labels_short = ["CB","Bkt","S1","S2","S3","CT"]
t_labels_long = ["Cryo Bottom","Bucket         ","Sensor 1      ",
                "Sensor 2      ","Sensor 3      ","Cryo Top Plate"]

####################################################################
# Create the GUI interface
####################################################################

# create a GUI (called root) and set its size
root = Tk.Tk()
root.geometry('800x600')

# create a figure on which to place 4 plots
fig = plt.Figure(figsize=(8,5.5))

# create a canvas for the figure and place it in the GUI
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=2, columnspan=3)

# set title of GUI
root.title(f"REMOTE Larpix Monitor (run started {start_date} at {start_time})")

# create buttons to quit or select temperature sensors
buttons()

####################################################################
# Create and place the level and temperature plots on the GUI
####################################################################

# create the level time-series plot
plotl = fig.add_subplot(221)                # place plot on upper left
plotl.set(title = "Level (mm)")
plotl.yaxis.set_major_formatter(FormatStrFormatter('% .0f'))
plotl.set_ylim(-10,310)

# create a meter plot inidicating the current level
ax1 = fig.add_subplot(223, polar = True)	# place plot on lower left
ax1.set_axis_off()

# create a bar chart for current temperatures
ax2 = fig.add_subplot(224)                  # place text on lower right
ax2.set_axis_off()                          # do not show axes
ax2.set_xlim(-210,40)

# create the temperature time-series plot 
plott = fig.add_subplot(222)                # place plot on upper right
plott.set(title = "Temperature (C)")
plott.yaxis.set_major_formatter(FormatStrFormatter('% .0f'))
plott.set_ylim(-210,50)

####################################################################
# create and plot vectors of stored data
####################################################################

# read time, level & 6 temperatures for each full set the content 
# of the data file. Any partial set recorded at the end of the content
# will be read later
for i in range(0,num_full_sets):
    times.append(float(content[file_line-1]))
    file_line+=1
    levels.append(float(content[file_line-1]))
    file_line+=1
    for j in range(0,6):
        new_ts[j].append(float(content[file_line-1]))
        file_line+=1

# plot the stored level data
plotl.plot(times, levels, "b")

# plot the stored temperature data in reverse order (to get legend lined
# from bottom of cryo to top
for i in reversed(range(0,6)):
    if sensors_live[i] == 1:
        plott.plot(times, new_ts[i], label=t_labels_short[i],
                    color=t_line_colors[i])
    else:
        plott.plot(0, 0, label=t_labels_short[i], color=t_line_colors[i])        

plott.legend(bbox_to_anchor=(1.2, 1), loc='upper right', fontsize="8")

####################################################################
# Continuously update all plots with new data from the lab
####################################################################

anil = animation.FuncAnimation(fig, update_plots, np.arange(1, 200), 
        interval=25, blit=False)

####################################################################
# Continuously update the GUI until it is closed by the user
####################################################################

Tk.mainloop()
