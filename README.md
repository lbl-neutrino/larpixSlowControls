**Larpix Slow Controls**

The code in this repository creates a user interface for monitoring larpix cryostat controls, including:  

/t (i) level of liquid, 

(ii) temperature at cryostat bottom, bucket bottom, cryostat top plate, and 3 optional temperature sensors which can be placed on test subjects

**To monitor the control sensors in the Larpix lab:**

Get onto the raspberry pi using a terminal window:  

  ssh -Y larpix@cryo-control.dhcp.lbl.gov

Enter password (IMPORTANT: The 2nd and 3rd digits are the numbers 1 and 0):  

  s10wcontrols

Go to the slowcontrols/ directory and run the python code for creating the GUI:  

  python3 gui_larpix_monitor.py

**To monitor the control sensors remotely:**

Step 1: At your remote location create a local git repository:

	git init

Step 2: Create the origin which tells your computer where to get this code:

	git remote add origin https://github.com/lbl-neutrino/larpixSlowControls.git

Step 3: pull the files in the Github repository into your remote git file (if it is not main then replace "main" below with your file path)

 	git pull origin main 

Step 4: there should be a new directory at your location called larpixSlowControls. Go into that directory and launch the remote python code. A dedicated terminal window is required for this purpose since python will ask you which data file you wish to read:

  	python3 remote_larpix_monitor.py

A promt will ask if you want to remotely monitor a live run:  

  (i) if you reply y (for yes) but there’s no live run in the lab you will get an error, 

  (ii) if you reply n (for no) you will be asked to supply a date in format yyyy_mm_dd. Check the data directory (instructions below) to see available dates.

**Data Directory:**

Data is stored both on the raspberry pi (at /data/) and on labpix (at /var/nfs/instrumentation_data/). While a live run is taking place in the lab, data will be stored in both places under a filename specifying the date the run was launched. Example:  

  larpix_history_2023_10_03.txt

You can view data in this file via the remote GUI, by following the instructions above for monitoring the control sensors remotely. Alternatively you can view a screenshot of the final GUI window in the plots directory (instructions below)

**Plots Directory:**

The final plots from previous runs are in a plots directory on both the raspberry pi (at /data/plots/) and on labpix (at /var/nfs/instrumentation_data/plots/). The files are labeled with the start date of the run. Example:  

  larpix_plots_2023_10_03.png

To view this plot from the terminal window:  

	gio open larpix_plots_2023_09_29.png

