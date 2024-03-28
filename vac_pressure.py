########################################################################
# Read 1 analog input from the Vacuum pressure gauge (using an ADS1115
# converter). Send data to InfluxDB, the data base on Labpix that feeds
# the Grafana control monitor.
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
GAIN = 1

# A lower data rate will provide less noise.
# Choices are 8, 16, 32, 64, 128 (default), 250, 475, 860 SPS
#   D_RATE (Signals/Sec)      NOISE (micro-V)
#            8                        3
#           128                      5-4
#           860                     10-8
DATA_RATE = 8

# resistors were used on the inputs to the ADC to divide the voltage
# down to levels the ADC can handle. The calibration constant removes
# the influence of the resistors
calibration = 10/21351

# initialize variables
pre_calibration, vac_pressure, calibrated_voltage, p1 = float(0.0), float(0.0), float(0.0), float(0.0)
conversion, a, b = 0, 0, 0

########################################################################
# establish InfluxDB connection
########################################################################

# sign into InfluxDB 
client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)

# prepare InfluxDB to accept data
write_api = client.write_api(write_options=SYNCHRONOUS)

########################################################################
#                               Main
########################################################################

while True:

    pre_calibration = adc.read_adc(0, gain=GAIN, data_rate=DATA_RATE)

    # back-out influence of resistor
    calibrated_voltage = (pre_calibration-13) * calibration

    # convert voltage from the Edwards-wrg200 pressure to pressure
    if calibrated_voltage > 10 or calibrated_voltage < 1.4:
        print(f"Out of range (1.4V, 10V) voltage = {calibrated_voltage}")
    elif calibrated_voltage > 2:
        a = 8.083
        b = 0.667
        conversion = 10 ** ((calibrated_voltage - a) / b)
    else:
        a = 6.875
        b = 0.600
        conversion = 10 ** ((calibrated_voltage - a) / b)

    vac_pressure = calibrated_voltage * conversion

    print(f"Pressure = {vac_pressure}")

    # create a data point (p) which identifies the measurement
    # category (measurement = "larpix_slow_controls"), name and value
    p1 = influxdb_client.Point(measurement).field("vac_pressure",vac_pressure)
        
    # push the point into the identified InfluxDB account
    write_api.write(bucket=bucket, org=ORG, record=p1)

    # Pause for 1 second
    time.sleep(1)
