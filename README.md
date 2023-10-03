**Larpix Slow Controls**
This code creates a GUI monitoring controls in the Larpix cryostat at Lbl, including:  

	(i) level of liquid, 

	(ii) temperature at cryostat bottom, bucket bottom, cryostat top plate, and 3 optional temperature sensors which can be placed on test subjects

**To monitor the control sensors in the Larpix lab:**
Get onto the raspberry pi using a terminal window:  

  ssh -Y larpix@cryo-control.dhcp.lbl.gov

Enter password (IMPORTANT: The 2nd and 3rd digits are the numbers 1 and 0):  
		s10wcontrols

Go to the slowcontrols/ directory and run the python code for creating the GUI:  
		python3 gui_larpix_monitor.py

**To monitor the control sensors remotely:**
In the same slowcontrols/ directory, run the code for creating a remote GUI. A dedicated terminal window is required for this purpose:  
		python3 gui_larpix_monitor.py

A promt will ask if you want to remotely monitor a live run:  
		(i) if you reply y (for yes) but there’s no live run in the lab you will get an error, 
		(ii) if you reply n (for no) you will be asked to supply a date in format yyyy_mm_dd. Check 
			the slowcontrols/data/ directory to see available dates for past runs

**Data Directory:**
While a live run is taking place in the lab, data will be stored in the slowcontrols/data directory under a filename specifying the date the run was launched. Example:  
		larpix_history_2023_09_29.txt

You can view data in this file via the GUI, by following the instructions above for monitoring the control sensors remotely. Alternatively you can see a screenshot of the final GUI window in the plots/ directory

**Plots Directory:**

The final plots from previous runs are in the slowcontrols/plots directory. They’re labeled with the start date of the run. Example:  
		larpix_plots_2023_09_29.png

To view this plot from the terminal window:  
		gio open larpix_plots_2023_09_29.png
