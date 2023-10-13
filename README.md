#################################################################################

**LARPIX SLOW CONTROLS** 

#################################################################################

The code in this repository creates a user interface for monitoring larpix cryostat controls, including:  

(i) level of liquid, 

(ii) temperature at cryostat bottom, bucket bottom, cryostat top plate, and 3 optional temperature sensors which can be placed on test subjects

The following steps must be followed to monitor Larpix controls. Complete instructions for each step are detailed in subsequent sections.

**Step 1:** Launch a monitoring session on the Larpix Raspberry Pi

**Step 2:** Connect your computer to the lab computer (Labpix)

**Step 3:** Launch the slow control dashboard

**Step 4:** When you're finished, stop the monitoring session

#################################################################################

**Step 1: LAUNCH A MONITORING SESSION ON THE LARPIX RASPBERRY PI** 

#################################################################################

To get onto the Larpix Raspberry Pi, go to the DUNE ND Electronics Development portal, and read the file entitled "Larpix Slow Controls Credentials".

**Only one monitoring session should be launched on the larpix raspberry pi at a time.** If you don't know if one is running, use the following query in your terminal window:

	ps -ef

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

If no session is already in progress, go to the /slowcontrols/ directory and run the following python code:

	python3 larpix_monitor.py

If the code is running successfully you will not see a response on your terminal window, but the data will begin to show up on the dashboard (Step 3).

#################################################################################

**Step 2: CONNECT YOUR COMPUTER TO THE LAB COMPUTER (LABPIX)**

#################################################################################

Connect a port on your computer to port 3000 on Labpix by typing the following text into a terminal window:

	ssh -L 2000:localhost:3000 username@labpix.dhcp.lbl.gov

Notes: Change to your username and if necessary, change the 2000 in this example to an open port on your computer. 

#################################################################################

**Step 3: LAUNCH THE SLOW CONTROL DASHBOARD**

#################################################################################

Open a web browser on your computer and go to the portal you configured in Step 2. In this example, you would type the following into your web browser:

	localhost:2000

You should be taken to the Grafana login page. The username and password are stored in the google docs file entitled "Larpix Slow Controls Credentials" on the DUNE ND Electronics Development portal.

At the top of the Grafana window is a search panel. Search for:

 	Larpix Slow Controls

You will see at least 2 choices: (i) Larpix Slow Controls - DO NOT EDIT, (ii) Larpix Slow Controls - Editable. If you wish to play with the dashboard go to the editable version. If you wish to save your changes to the dashboard please save a version under your own name. For example, you probably see one already named "Larpix Slow Controls - cmcnulty". You can save your version by clicking on the gear symbol at the top of the page which will take you to a new page where you can configure certain parameters and then click on the "Save as" button at the top. 

#################################################################################

**TO STOP THE RUN** 

#################################################################################

You must be on the raspberry pi (instructions above) to stop the run. Type the follwoing into a terminal window:

	ps -ef

Amongst the resulting list, look for a line with "larpix_monitor.py" on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

In this example, you would type "kill 13762 <return>" in the terminal window. 
