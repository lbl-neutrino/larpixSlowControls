#################################################################################

**LARPIX SLOW CONTROLS** 

#################################################################################

The code in this repository creates a user interface for monitoring larpix cryostat controls, including:  

(i) level of liquid, 

(ii) temperature at cryostat bottom, bucket bottom, cryostat top plate, and 3 optional temperature sensors which can be placed on test subjects

(iii) pressure inside cryostat

(iv) high-voltage and/or current supplied to a test subject such as a TPC (this is optional depending on the test being performed)

The following steps are taken to monitor Larpix controls. Each step is detailed in subsequent sections.

**Step 1:** Turn on the pi's and pressure guage

**Step 2:** Launch a monitoring session on the cryo-control Raspberry Pi

**Step 3 (optional):** Launch the monitoring of high voltage on the drizzle Raspberry Pi

**Step 4:** Connect your computer to the lab computer (Labpix)

**Step 5:** Launch the slow control dashboard

**Step 6:** When you're finished, stop the monitoring session

#################################################################################

**Step 1: TURN ON THE PIS AND PRESSURE GUAGE** 

#################################################################################

If you do not turn on all 3 of the following devices the monitoring python code will not run.

- The cryo-control Raspberry Pi is sitting ontop of the cryostat with a power button on its case. 

- The hv-control Raspberry Pi is sitting ontop of the Spellman power supply in the rack next to the cryostat. Its power button is on its power cable which is strapped to the rack just next to the pi. This pi should be turned on whether or not you are supplying voltage and/or current to your test subject. 

- A pressure guage control monitor is mounted to the top of the cryostat with its own power button.

#################################################################################

**Step 2: LAUNCH A MONITORING SESSION ON THE cryo-control RASPBERRY PI** 

#################################################################################

The cryo-control pi is used to monitor all controls other than the voltage and/or current supplied to a test subject. 

Instructions for logging into the cryo-control Raspberry Pi are in the file: DUNE ND Electronics Development/Control Monitors/Larpix/Larpix Slow Controls Credentials

**Only one monitoring session should be launched at a time.** Use the following query in your terminal window to see if one is already running:

	ps -ef

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

If no session is already in progress, go to the /slowcontrols/ directory on the Pi and run the following python code:

	python3 larpix_monitor.py

If the code is running successfully you may not see a response on your terminal window, but the data will begin to show up on the dashboard (Step 5).

#################################################################################

**Step 3 (optional): LAUNCH A MONITORING SESSION ON THE hv-control RASPBERRY PI** 

#################################################################################

The hv-control pi is used to monitor the voltage and/or current supplied to a test subject. 

Instructions for logging into the hv-control Raspberry Pi are in the file: DUNE ND Electronics Development/Control Monitors/Larpix/Larpix Slow Controls Credentials

**Only one monitoring session should be launched at a time.** Use the following query in your terminal window to see if one is already running:

	ps -ef

Amongst the resulting list, look for a line with "hv_read_write.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 hv_read_write.py

If no session is already in progress, go to the /high-voltage/ directory on the Pi and run the following python code:

	python3 hv_read_write.py

If the code is running successfully you may not see a response on your terminal window, but the data will begin to show up on the dashboard (Step 5).

#################################################################################

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

**Step 6: TO STOP THE MONITORING SESSION** 

#################################################################################

You must be on the cryo-control raspberry pi (instructions above) to stop the monitoring session. Type the follwoing into a terminal window:

	ps -ef

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

In this example, you would type "kill 13762 <return>" in the terminal window to stop the monitoring session.

Follow the same steps on the hv-control raspberry pi to kill hv_read_write.py
