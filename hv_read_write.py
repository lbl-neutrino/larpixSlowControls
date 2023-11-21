########################################################################
# Read 4 analog inputs from the Spellman voltage power supply (using 
# an ADS1x15 converter) and send data to InfluxDB, the data base on 
# Labpix that feeds the Grafana control monitor.
# 
#                             ANALOGUE INPUTS
#   ADC Input       Value       Spellman Pin   Wire Color   Python List
#
#      A0   =   current reading       TB5         orange     voltage[0]
#      A1   =   voltage reading       TB6         blue       voltage[1]
#      A2   =   current setting       TB9         green      voltage[2]
#      A3   =   voltage setting       TB11        red        voltage[3]
########################################################################

import time

# Import ADS1x15 command library to read high voltages via ADC
import Adafruit_ADS1x15

# influxDB is the database on labpix connected to grafana (the graphical
# interface used to monitor slow controls)
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

########################################################################
# Initialize variables
########################################################################

# shorten the prefix for ADS1115 commands
adc = Adafruit_ADS1x15.ADS1115()

# Identify the InfluxDB account name (org), password (token), InfluxDB 
# portal (url), and the InfluxDB path for voltage data (tagged with 
# bucket, measurement and field)
ORG = "lbl-neutrino"
TOKEN = "-IkZYxHAAahMAM_11tBbmtxr3tKpF7gC4wMlRZgw2rW6Fm-Ifykrt8ZgOo3c_h2jUYD3hNSp5FHr_IqtuXlCgw=="
URL = "http://labpix.dhcp.lbl.gov:8086"
bucket = "cryostat-sensors"
measurement = 'larpix_slow_controls'

# set gain appropriate for range of input voltages:
#   GAIN     RANGE
#  - 2/3    +/-6.144V
#  -   1    +/-4.096V
#  -   2    +/-2.048V
#  -   4    +/-1.024V
#  -   8    +/-0.512V
#  -  16    +/-0.256V
GAIN = 2

# A lower datat rate will provide less noise. 
# Choices are 8, 16, 32, 64, 128 (default), 250, 475, 860 SPS
#   D_RATE (Signals/Sec)      NOISE (micro-V)
#            8                        3
#           128                      5-4
#           860                     10-8
DATA_RATE = 8

# calibration constants for voltage measurements are slightly different
# because resistors (on ADC) are slightly different
calibrations = [0,0,0,0]
calibrations[0] = 1/3201.9
calibrations[1] = 1/3201.3
calibrations[2] = 1/3210.3
calibrations[3] = 1/3207.6

# voltage and current readings from pins on back of power supply must be 
# converted to get the actual voltage and current sent inside cryo 
conversions =  [0.0333/1_000_000, 3, 0.0333/1_000_000, 3]

# create 2 lists of voltage values
pre_calibrations = [0]*4
voltages = [0]*4
resistance = 0

# create names for the voltage values
voltage_labels = ["current_reading", "voltage_reading", "current_setting",
                  "voltage_setting"]

########################################################################
# establish InfluxDB connection
########################################################################

# sign into InfluxDB 
client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)

# prepare InfluxDB to accept data
write_api = client.write_api(write_options=SYNCHRONOUS)

########################################################################
# Main
########################################################################

while True:

    for i in range(4):
        pre_calibrations[i] = adc.read_adc(i, gain=GAIN, data_rate=DATA_RATE)

        # Calibrate for resistor variation and pin-to-actual values
        voltages[i] = pre_calibrations[i] * calibrations[i] * conversions[i]

        # create a data point (p) which identifyies the measurement
        # category (measurement = "larpix_slow_controls"), name and value
        p1 = influxdb_client.Point(measurement).field(voltage_labels[i], 
            voltages[i])
        
        # push the point into the identified InfluxDB account 
        write_api.write(bucket=bucket, org=ORG, record=p1)

    # use "try" to avoid dividing by zero if no current is detected
    try: 

        # measure resistance along cable carrying current btwn cathode & anode) 
        resistance = voltages[1] / voltages[0]

        # push resistance to influxdb using the point p2
        p2 = influxdb_client.Point(measurement).field("resistance", 
              resistance)
        write_api.write(bucket=bucket, org=ORG, record=p2)

    except:
        print("Encountered zero value for current = ", voltages[0])

    # Pause for 1 second
    time.sleep(1)
