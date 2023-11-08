#################################################################################

**LARPIX SLOW CONTROLS** 

#################################################################################

The code in this repository creates a user interface for monitoring larpix cryostat controls, including:  

(i) level of liquid, 

(ii) temperature at cryostat bottom, bucket bottom, cryostat top plate, and 3 optional temperature sensors which can be placed on test subjects

(iii) pressure differential inside cryostat

(iv) flow of liquid through the purifying filter

(v) voltage and current supplied to a test cube (optional) 

A monitoring session involves the following steps (each detailed in subsequent sections).

**Step 1:** Supply power to the Pi's and pressure guage

**Step 2:** Launch a monitoring session on the cryo-control Pi

**Step 3 (optional):** Launch a monitoring session on the hv-control Pi

**Step 4:** Connect your computer to the lab computer (Labpix)

**Step 5:** Launch the slow control dashboard

**Step 6:** When you're finished, stop the monitoring session

#################################################################################

**Step 1: SUPPLY POWER TO THE PI(S) AND PRESSURE GUAGE** 

#################################################################################

If you don't turn on the following 3 devices, the python code may print out an error and refuse to run. 

- The "cryo-control Raspberry Pi" sits on top of the cryostat with a power button on it's case. 

- The "hv-control Raspberry Pi" sits on top of the Spellman high voltage supply unti in the rack next to the cryostat. The pi's power button is on the power cable strapped onto the rack. 

- The pressure guage is mounted on the top of the cryostat.

#################################################################################

**Step 2: LAUNCH A MONITORING SESSION ON THE CRYO-CONTROL PI** 

#################################################################################

The cryo-control Pi reads temperatures, liquid level, pressure and liquid flow rate inside the larpix cryostat. Instructions for logging onto the cryo-control Pi are in the file DUNE ND Electronics Development/Control Monitors/Larpix Slow Controls Credentials

**Only one monitoring session should be launched at a time.** Use the following query in your terminal window to see if one is already running:

	ps -ef

 Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

If no session is already in progress, go into the /slowcontrols/ directory on the Pi and run the following python code:

	python3 larpix_monitor.py

If the code is running successfully you may not see a response on your terminal window, but the data will begin to show up on the dashboard (Step 5).

#################################################################################

**Step 3 (optional): LAUNCH A MONITORING SESSION ON THE HV-CONTROL PI** 

#################################################################################

If you are not supplying voltage and/or current to your test subject (such as a TPC module), then skip this step. Instructions for logging onto the cryo-control Pi are in the file DUNE ND Electronics Development/Control Monitors/Larpix Slow Controls Credentials

**Only one monitoring session should be launched at a time.** Use the following query in your terminal window to see if one is already running:

	ps -ef

Amongst the resulting list, look for a line with "hv_read_write.py" on the end. Example:

	larpix     2466   2443 1 11:15 pts/0    00:00:22 python3 hv_read_write.py

If no session is already in progress, go into the /high-voltage/ directory on the Pi and run the following python code:

	python3 hv_read_write.py

If the code is running successfully you may not see a response on your terminal window, but the data will begin to show up on the dashboard (Step 4).

################################################################################

**Step 4: CONNECT YOUR COMPUTER TO THE LAB COMPUTER (LABPIX)**

#################################################################################

Connect a port on your computer to port 3000 on Labpix by typing the following text into a terminal window:

	ssh -L 2000:localhost:3000 username@labpix.dhcp.lbl.gov

Notes: Change to your username and if necessary, change the 2000 in this example to any open port on your computer. 

#################################################################################

**Step 5: LAUNCH THE SLOW CONTROL DASHBOARD**

#################################################################################

Open a web browser on your computer and go to the portal you configured in Step 4. In this example, you would type the following into your web browser:

	localhost:2000

You should be taken to the Grafana login page. The username and password are stored in the file DUNE ND Electronics Development/Control Monitors/Larpix Slow Controls Credentials.

At the top of the Grafana window is a search panel. Search for:

 	Larpix Slow Controls

You will see at least 2 choices: (i) Larpix Slow Controls - DO NOT EDIT, (ii) Larpix Slow Controls - Editable. If you wish to play with the dashboard go to the editable version. If you wish to save your changes to the dashboard please save a version under your own name. For example, "Larpix Slow Controls - cmcnulty". Save your version by clicking on the gear symbol at the top of the dashboard. This will take you to a new page where you can configure certain parameters. Click on the "Save as" button at the top. 

#################################################################################

**Step 6: WHEN YOU ARE FINISHED, STOP THE MONITORING SESSION** 

#################################################################################

You must be on the raspberry pi(s) (instructions above) to stop the run. Type the follwoing into a terminal window:

	ps -ef

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

In this example, you would type "kill 13762 <return>" in the terminal window to stop the monitoring session.

If you are also monitoring voltage and/or current, kill the hv_read_write.py program on the hv_control Pi by following the same steps as above.
