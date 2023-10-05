#################################################################################

**LARPIX SLOW CONTROLS** 

#################################################################################

The code in this repository creates a user interface for monitoring larpix cryostat controls, including:  

(i) level of liquid, 

(ii) temperature at cryostat bottom, bucket bottom, cryostat top plate, and 3 optional temperature sensors which can be placed on test subjects

#################################################################################

**TO MONITOR CONTROLS LIVE ON LARPIX RASPBERRY PI** 

#################################################################################

Get onto the raspberry pi using a terminal window:  

  	ssh -Y larpix@cryo-control.dhcp.lbl.gov

Enter password (IMPORTANT: The 2nd and 3rd digits are the numbers 1 and 0):  

	s10wcontrols

**Only one monitor should be launched on the larpix raspberry pi at a time.** If one is already running, launch your monitor from labpix instead (instructions below). If you don't know if one is running, use the following query in your terminal window:

	ps -ef

Amongst the resulting list, look for the following python3 script:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 gui_larpix_monitor.py

You can either launch your monitor on labpix or kill this run (in this case kill 13762) and start a new one. 

To start a new run, go to the /slowcontrols/ directory and run the python code for creating the GUI:  

	python3 gui_larpix_monitor.py

#################################################################################

**TO MONIOR LIVE OR HISTORICAL DATA ON LABPIX**

#################################################################################

On labpix you can monitor controls from a live or historical run. If you haven't done so already, go to a .git repository and clone the larpixSlowControls repository from Github:

	git clone https://github.com/lbl-neutrino/larpixSlowControls.git

The cloning process will create a new directory called /larpixSlowControls/. Go into that directory and run the following code (note, a dedicated terminal window is required for this purpose since python will prompt you for input):

  	python3 remote_larpix_monitor.py

A promt will ask if you want to remotely monitor the latest run:

  (i) if you reply y (for yes) you will see the latest data. If the latest data is from a run that has ended, the monitor will display the message "Lab run has finished". In this case, if you wish to instigate a new run from the raspberry pi follow the directions above.

  (ii) if you reply n (for no) you will be asked to supply a date in format yyyy_mm_dd. Check the data directory (instructions below) to see available dates.

##################################################################################

**DATA DIRECTORY:**

##################################################################################


Data is stored both on the raspberry pi (at /data/) and on labpix (at /var/nfs/instrumentation_data/) while the live run is progressing. The file name will specify the date the run was launched. Example:  

	larpix_history_2023_10_03.txt

You can view data from a live or historical run from labpix (instructions above).

##################################################################################

**SELECTING WHICH SENSORS TO DISPLAY** 

##################################################################################

Data is collected and stored from all 6 temperature sensors. Three of the sensors are always shown (Cryo Bottom, Bucket Bottom, Cryo Top Place), but the user can choose which optional sensors (S1, S2, S3) to graph on the user interface, using the button at the top of the monitor "Select Temperature Sensors". 

#################################################################################

**TO STOP THE RUN** 

#################################################################################

When you stop the run, python writes "end" to the last line of the data file. You must be on the raspberry pi (instructions above) to stop the run. You can either use the "Quit Larpix Monitor" button at the top of the primary monitor gui, or run the following query in a terminal window:

	ps -ef

Amongst the resulting list, look for the following python3 script:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 gui_larpix_monitor.py

In this case, you would type "kill 13762 <return>" in the terminal window.

#################################################################################

**PLOTS DIRECTORY:**

#################################################################################

When a run is over the final plots are sent to the /plots/ directory on both the raspberry pi (at /data/plots/) and on labpix (at /var/nfs/instrumentation_data/plots/). The graphic files are labeled with the start date of the run. Example:  

	larpix_plots_2023_10_03.png

To view a plot from the terminal window:  

	gio open larpix_plots_2023_09_29.png
