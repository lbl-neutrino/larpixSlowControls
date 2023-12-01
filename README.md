#################################################################################

**Bldg 70/141 LARPIX SLOW CONTROLS** 

#################################################################################

The code in this repository creates a user interface for monitoring Building 70/141 cryostat controls, including:

(i) liquid level, 

(ii) temperature on 6 sensors

(iii) pressure inside cryostat

(iv) high-voltage and/or current supplied to a test subject (optional)

(v) power supplied to heating strips

Steps (detailed below) to monitor Larpix controls include:

**Step 1:** Turn on two Raspberry Pi's and pressure guage

**Step 2:** Launch monitoring session on cryo-control Raspberry Pi

**Step 3 (optional):** Launch high voltage monitoring on hv-control Raspberry Pi, then turn on HV supply

**Step 4:** Connect port on your computer to localhost:3000 on Bldg 70/141 Labpix

**Step 5:** Launch the Larpix Slow Control dashboard

**Step 6:** When you're finished testing, turn on heating strips 

**Step 7:** Stop monitoring when cryo temp reaches room temp

#################################################################################

**Step 1: TURN ON THE TWO PIS AND PRESSURE GUAGE** 

#################################################################################

If you do not provide power to the following devices the python code may not run.

- cryo-control Raspberry Pi sits ontop of cryostat with power button on its case

- hv-control Raspberry Pi sits ontop of Spellman power supply in rack next to cryostat. The power button is on its power cable (strapped to rack just next to pi). Turn on pi whether or not you're supplying voltage or current to test subject.

- Pressure guage monitor is mounted to cryostat top with a power button.

- The Rigol power supply sits on the shelf above the bench next to the cryostat (facing the door). Make sure it is turned OFF if you do not wish to supply power to the heating strips.

#################################################################################

**Step 2: LAUNCH A MONITORING SESSION ON cryo-control RASPBERRY PI** 

#################################################################################

cryo-control pi is used to monitor all controls other than the high-voltage/current supplied to test subjects. 

Instructions for logging into the cryo-control Raspberry Pi are in the file: DUNE ND Electronics Development / Operations / Bldg 70/141 / 70/141 Credentials Database Dashboard Pi 

**Only one monitoring session should be launched at a time.** Check to see if a monitoring screen named larpix-control is already running:

	screen -list

If not, create a new one:

	screen -S larpix-control

Alternatively you can connect to an exiting screen:

	screen -xS larpix-control

Double check to make sure the monitoring python code is not already running on someone elses terminal:

	ps -a 

If there is more than one python process running, get the name of the files running:

	ps -ef 

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

Kill any code running outside of the larpix-control screen. In this example:

	kill 13762

To start a new monitoring session (in the larpix-control screen), go into the slowcontrols/ directory and type:

	python3 larpix_monitor.py

If the code is running successfully you may not see a response on your terminal window, but the data will begin to show up on the dashboard (Step 5).

To exit the larpix-control screen:

 	hit Ctrl+a and then d

#################################################################################

**Step 3 (optional): LAUNCH A MONITORING SESSION ON THE hv-control RASPBERRY PI** 

#################################################################################

The hv-control pi is used to monitor the voltage and/or current supplied to test subjects. If the Spellman HV supply is not turned on, the python code will not run. 

Instructions for logging into the hv-control Raspberry Pi are in the file: DUNE ND Electronics Development/Control Monitors/Larpix/Larpix Slow Controls Credentials

**Only one monitoring session should be launched at a time.** 

Follow the same instructions as in Step 2, replacing the accessable screen name with "hv-control" and the python script with "hv_read_write.py"

#################################################################################

**Step 4: CONNECT YOUR COMPUTER TO THE Bldg 70/141 LAB COMPUTER (LABPIX)**

#################################################################################

If you wish to launch a monitor on labpix you can skip this step. 

If you wish to lauch a monitor on a local computer, connect a port on your computer to port 3000 on Labpix by typing the following text into a terminal window:

	ssh -L 2000:localhost:3000 username@labpix.dhcp.lbl.gov

Notes: Change to your username and if necessary, change the 2000 in this example to any open port on your computer. 

#################################################################################

**Step 5: LAUNCH THE Bldg 70/141 SLOW CONTROL DASHBOARD**

#################################################################################

Open a web browser on your computer (or labpix) and go to the portal you configured in Step 4. In this example, you would type the following into your web browser address line:

	localhost:2000

You should be taken to the Grafana login page. The username and password are stored in the file DUNE ND Electronics Development/Control Monitors/Larpix Slow Controls Credentials.

At the top of the Grafana window is a search panel. Search for:

 	Larpix Slow Controls

You will see at least 2 choices: (i) Larpix Slow Controls - DO NOT EDIT, (ii) Larpix Slow Controls - Editable. If you wish to play with the dashboard go to the editable version. If you wish to save your changes please save a version under your own name. For example, "Larpix Slow Controls - cmcnulty". Save your version by clicking on the gear symbol at the top of the dashboard. This will take you to a new page where you can configure certain parameters. Click on the "Save as" button at the top. 

#################################################################################

**Step 6: WHEN YOU'RE FINISHED TESTING, TURN ON HEATING STRIPS** 

#################################################################################

A Rigol DP932U power supply sits on the shelf above the bench next to the cryostat (facing the door). It's connected to two heating strips inside the cryo via 4 wires plugged into channels 1 and 2. These heating strips will speed up the liquid evaporation process when you are finished with your tests. 

Turn on the power supply and set the voltage and current on both channels to:

	Heat-strip voltage = 32V
	
	Heat-strip current = 3A

Get onto the larpix-control screen on the cryo-control raspberry pi following instructions in Step 2:

	screen -xS larpix-control

To turn on the heating strips (in the larpix-control screen), go into the slowcontrols/ directory and type:

	python3 heat_on.py

If the code is running successfully the power data will be displayed on the dashboard.

The power to the heating strips should turn off automatically when the temperature sensor on either the top plate or bottom of cryo reaches 273 K. However, someone should monitor the temperature and power to the strips in case the automatic shut off mechanism malfunctions. 

To exit the larpix-control screen:

 	hit Ctrl+a and then d

#################################################################################

**Step 7: STOP THE MONITORING SESSION** 

#################################################################################

Continue monitoring until the temperature in the cryostat has reached a safe level to open the lid (we suggest T > 273K).

You must be on the cryo-control raspberry pi (instructions above) to stop the monitoring session. Get on the accessable screen running the monitoring code:

	screen -xS larpix-control

Type the follwoing into the terminal window:

	ps -ef

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

Stop the monitoring code (using this example):

	kill 13762

Follow the same steps to kill "heat_on.py"

Kill the accessable screen:

	<Ctl>+a k

If applicable, follow the same steps on the hv-control raspberry pi to kill "hv_read_write.py"
