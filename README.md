# Building 70-141 CRYOSTAT SLOW CONTROLS

This code creates a user interface for monitoring Building 70/141 cryostat controls, including the liquid level, temperature on 6 sensors, pressure inside cryostat, high-voltage and/or current supplied to a test subject (optional), and power supplied to heating strips.

Steps (detailed below) to monitor Blg 70-141 cryostat controls include:

- **Step 1:** Turn on devices

- **Step 2:** Launch monitoring code

- **Step 3 (optional):** launch high voltage code

- **Step 4:** Connect to labpix

- **Step 5:** Launch the dashboard

- **Step 6:** When finished, turn on heating strips 

- **Step 7:** Stop monitoring when cryo temp reaches room temp

- **Troubleshooting**

## Step 1: TURN ON DEVICES

If you do not provide power to the following devices the python code may not run.

- cryo-control Raspberry Pi sits ontop of cryostat with power button on its case

- hv-control Raspberry Pi sits ontop of Spellman power supply in rack next to cryostat. The power button is on its power cable (strapped to the rack).

- Pressure guage monitor is mounted to cryostat top with its own power button

- The Rigol power supply for the heating strips sits on the shelf above the bench next to the cryostat (facing the door). Make sure it is turned ON and set to V=0 and I=0 (unless you're ready to turn on the heaters)

## Step 2: LAUNCH A MONITORING SESSION

The cryo-control raspberry pi is used to monitor temperature, level, pressure and heat strip power.

See Pi login instructions at: `DUNE ND Electronics Development / Operations / Bldg 70-141 / 70/141 Credentials Database Dashboard Pi` 

**Only one monitoring session should be launched at a time.** Check to see if a monitoring screen named `larpix-control` is already running:

	screen -list

If not, create a new screen:

	screen -S B70-control

Alternatively connect to an exiting screen:

	screen -x B70-control

Make sure the python code is not already running:

	ps -a 

If there is more than one python process, get the name of the files:

	ps -ef 

Amongst the resulting list, look for a line with `larpix_monitor.py` on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

Kill any code running outside of the larpix-control screen. In this example:

	kill 13762

In the `slowcontrols/` directory launch a new monitoring session (in larpix-control screen!)

	python3 larpix_monitor.py

If the code is running successfully, the data will show up on the Grafana monitoring dashboard (Step 5).

To exit the larpix-control screen hit:

 	Ctrl+a d

## Step 3 (optional): LAUNCH High Voltage Controls

The hv-control raspberry pi is used to monitor the voltage and/or current supplied to test subjects. If the Spellman HV supply is not turned on, the python code will not run. 

Instructions for logging into the hv-control Raspberry Pi are in the file:  `DUNE ND Electronics Development / Operations / Bldg 70/141 / 70/141 Credentials Database Dashboard Pi` 

**Only one monitoring session should be launched at a time.** 

Follow Step 2 again, but use the screen name `hv-control` and python code `hv_read_write.py`

## Step 4: CONNECT to LABPIX

If you're working on labpix, skip this step. 

In a terminal window, connect a port on your computer to port 3000 on Labpix:

	ssh -L 3000:localhost:3000 username@labpix.dhcp.lbl.gov

Notes: Change to your username and if necessary, change the 1st 3000 in this example to any open port on your computer. 

## Step 5: LAUNCH THE DASHBOARD

In your web browser address line open the portal:

	localhost:3000

Grafana's username and password are stored in: `DUNE ND Electronics Development/Control Monitors/Larpix Slow Controls Credentials`.

Click on the 3 lines in the far-left upper corner next to `Home`. Choose `Dashboards`. There will be 2 folders. Go into the folder named `B70-141`. 

You will see at least 2 choices: `Larpix Slow Controls - DO NOT EDIT`, or `Larpix Slow Controls - Editable`. If you wish to play with the dashboard go to the editable version. You can save your changes using your own name. For example, 'Larpix Slow Controls - cmcnulty'. Save your version by clicking on the gear symbol at the top of the dashboard. This will take you to a new page where you can configure certain parameters. Click on the "Save as" button at the top. 

## Step 6: WHEN FINISHED, TURN ON HEATING STRIPS

A Rigol DP932U power supply sits on the shelf above the bench next to the cryostat. It's connected to two heating strips inside the cryo via 4 wires plugged into Rigol channels 1 and 2. These heating strips will speed up the liquid evaporation process when you are finished testing. 

(i) Kill the monitoring process launched in Step 2 (python code `larpix_monitor.py`), and turn off the cryo-control Raspberry Pi. Turn off the Rigol power supply. These steps are necessary to break the remote connection between the Pi and the Rigol.

(ii) Turn the Rigol back on, 

(iii) set the voltage and current on both channels to: voltage = 32V and current = 3A. 

(iii) Turn on both channel 1 and 2.

Turn the cryo-control Pi back on and relaunch the python code `larpix_monitor.py`.

If the code is running successfully, the monitoring dashboard should indicate power to the heating strips of ~70W.

The power to the heating strips should turn off automatically when the temperature sensor on either the top plate or bottom of cryo reaches 200 K. However, someone should monitor the temperature and power to the strips in case the automatic shut off mechanism malfunctions. 

## Step 7: STOP THE MONITORING SESSION

Continue monitoring until the temperature in the cryostat has reached a safe level to open the lid (we suggest T > 273K).

You must be on the cryo-control raspberry pi (instructions above) to stop the monitoring session. 

Type the follwoing into the terminal window:

	ps -ef

Amongst the resulting list, look for a line with `larpix_monitor.py` on the end. Example:

	larpix     13762   13743 29 07:11 pts/1    00:00:11 python3 larpix_monitor.py

Stop the monitoring code (using this example):

	kill 13762

Follow the same steps to kill `heat_on.py`

Follow the same steps on the hv-control raspberry pi to kill `hv_read_write.py`

## Trouble Shooting

### Python Code
If the monitoring code won't launch make sure all devices are turned on (step 1). 

### Grafana 
If Grafana tells you it can not retrieve data, check to make sure that the session on your local terminal window ("ssh"ing into the computer hosting Grafana) is still active. 

If Grafana is consuming too much CPU, first try killing the monitoring python code and relaunching it. If that doesn't work, kill Grafana and restart it by using:

	 sudo systemctl restart grafana-server

In general the same restart command can be used if Grafana isn't running (i.e.  if port 3000 doesn't automatically take you to Grafana).

### InfluxDB

To start (or restart) InfluxDB, log onto labpix. Make sure you're in the right directory

	cd /

The command to restart InfluxDB must be run as mkramer (impersonating Matt Kramer):

 	sudo su mkramer 

 	podman start influx_matt 

If you want to restart influx, just type "restart" instead of "start" in the podman command above. 

If sending data to InfluxDB is causing timeout errors, put the following script around the code where the errors tend to occur.

	import urllib3

	try:
   	    <problematic code giving timeout errors ... for example, a write command to InfluxDB>
	except urllib3.exceptions.ReadTimeoutError:
    	    continue 

Two python scripts cannot use same 8086 port for InfluxDB. Instead set up separate containers by following these steps: 

(i) create a directory for Influx's storage: 

 	mkdir -p ~/data/hv_influx 
 
(ii) launch a container: 

	podman run -d --name influx_hv -p 28086:8086 -v ~/data/hv_influx:/var/lib/influxdb2 docker.io/influxdb:2.7.3 
 
The -p 28086:8086 tells podman to route labpix's port 28086 to the container's port 8086. Eventually we could potentially have slow controls, HV, and pacmon all on a single instance (perhaps with separate buckets). But while we're still in the development phase, it's safer to have separate instances.

(iii) Point a browser to port 28086 and go through the initial setup screen to create a new InfluxDB account (w username/password/token)
