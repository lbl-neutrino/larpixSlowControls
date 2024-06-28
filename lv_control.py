########################################################################
# The Wiener PL506 power supply is used to provide 24V to a pacman.
# This code currently initializes the PL506, reads (and sends to 
# InfluxDB) voltages every 10s
########################################################################

import time

# influxDB is the database connected to grafana (the graphical
# interface used to monitor B70 slow controls and DQM)
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# os is used to issue system commands (in this case SNMP commands) via
# python code, as needed to initialize the Wiener PL506
import os

# subprocess is needed to assign SNMP command outputs to variables for 
# sending to InfluxDB
import subprocess

# urllib3 has functions that will help with timeout url problems
import urllib3

#######################################################################
# Assign global variables
#######################################################################

# Identify the InfluxDB account name (org), password (token), InfluxDB 
# portal (url), and the InfluxDB path for voltage data (tagged with 
# bucket, measurement and field)
ORG = "lbl-neutrino"
TOKEN = "JRS1O-0BiJ-2dwz1pIaWobkKkYoXS3oN0GD9UJea22jvqwp6H1mvLvNzw3naahbSF7UxnD8PdMgmT3E4XdTerw=="
URL = "http://labpix.dhcp.lbl.gov:28086"
bucket = "hv-controls"
measurement = 'readings-settings'

# create name for the voltage value in InfluxDB
voltage_label = "voltage_reading"

# voltage is used to read from PL506 and write to InfluxDB
voltage = 0.0

#######################################################################
# Initialize the PL506 power supply and the Influx database
#######################################################################

# turn on the Wiener PL506 power supply
cmd = "snmpset -v 2c -m+WIENER-CRATE-MIB -c private 192.168.1.2 sysMainSwitch.0 i 1"
os.system(cmd)

# turn on chosen channel(s)
cmd = "snmpset -v 2c -m+WIENER-CRATE-MIB -c guru 192.168.1.2 outputSwitch.u0 i 1"
os.system(cmd)

# set the desired voltage on the chose channel(s)
cmd = "snmpset -v 2c -m+WIENER-CRATE-MIB -c guru 192.168.1.2 outputVoltage.001 F 24.0"
os.system(cmd)

# sign into InfluxDB 
client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)

# prepare InfluxDB to accept data
write_api = client.write_api(write_options=SYNCHRONOUS)

#######################################################################
# main
#######################################################################

while(True):

	# the subprocess commands aren't like the "os" commands. They 
	# require a set of arguments to be sent to the snmp command, hence 
	# the following change in format 
	snmp_cmd = ["snmpget", "-v", "2c", "-m+WIENER-CRATE-MIB", "-c", "public", "192.168.1.2", "outputVoltage.001"]

	# the other arguments below are needed to capture the output in 
	# a variable instead of it going straight to the screen
	cmd_info = subprocess.run(snmp_cmd, check=False, capture_output=True)

	# various information results from the command, we're only interested
	# in the output (hence the "stdout"). Without the "decode" the 
	# would output ones and zeros. 
	output_string = cmd_info.stdout.decode()

	# the output string has a lot of information, we only need the voltage
	# which must be converted to an integer
	voltage = float(output_string[52:58])
	print(f"The voltage is {voltage}")

	# create a data point (p) which identifyies the measurement
	# category (measurement is assigned earlier), name and value
#    	 p = influxdb_client.Point(measurement).field(voltage_label, voltage)
#	 try:
        # push the point into the identified InfluxDB account 
#        	write_api.write(bucket=bucket, org=ORG, record=p1)

#    	 except urllib3.exceptions.ReadTimeoutError:
#        	continue

	time.sleep(10)

