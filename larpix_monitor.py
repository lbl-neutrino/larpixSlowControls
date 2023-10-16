####################################################################
# Monitor the temperature, level of liquid and pressure in the larpix
# cryostat. Write the data to the InfluxDB database on labpix
####################################################################

# used to get mean and median of ADC readings
import numpy as np

# influxDB is the database on labpix used by grafana
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# An SPI (Serial Peripheral Interface bus) transports information to or 
# from the AD7124-8 (temperature sensors)
import spidev
spi = spidev.SpiDev()           # abbreviate spidev

# serial is used to read/write data to the pressure gauge through the
# raspberry pi's USB port
import serial

######################################################################
# Functions
######################################################################

# Read the level of liquid in the Larpix Cryostat, by reading a CDC 
# (capacitance to digital converter). To improve precision this routine 
# reads capacitance 10 times, takes the median of every 5, and then 
# averages the medians.
def read_cdc():

    num_test = 10                           # number of cdc readings
    num_median = 5                          # size of the median set
    caps, median_levels = [], []
    cap, i, median_cap, level = 0,0,0,0

    # used to calibrate levels to capacitance
    sensor_length = 300
    min_cap = 1.0646713
#    max_cap = 9.5106614                    # small bucket w sensor diagonal
    max_cap = 3.3422823                     # large bucket w sensor vertical

    while len(caps) < num_test:             # read capacitance from cdc
        val = bus.read_i2c_block_data(i2c_addr,0,19)
        if val[0] != 7:                     # val[0]=7 is old data
            cap = val[1]*2**16 + val[2]*2**8 + val[3]
            caps.append(cap)

    for i in range(0,len(caps),num_median):  # reduce noise using median

        # check to see if you have enough values left to get a median
        if len(caps[i:i+num_median]) < num_median:
            break                           # if not exit the function

        # measure median capacitance
        median_cap = np.median(caps[i:i+num_median])/1e6

        # transform capacitance into length
        median_level = (median_cap - min_cap) * sensor_length / (max_cap 
                        - min_cap)

        # add the new value to the list of median levels
        median_levels.append(median_level)

    # take the mean of median levels
    level = np.mean(median_levels)
    return level

# get a new temperature reading from the ADC
def read_adc():

    # initialize variables
    global t_start, new_ts
    write = 0
    read = 1            # command to read from ADC
    address_status = 0  # ADC status is available on register 0
    address_data = 2	# ADC Data is available on register 2
    address_ch0 = 9
    decimal_result = 0
    temperatures = [0,0,0,0,0,0]

    # 6 sensor register settings: enable, Ain positive, Ain negative
    sensor_inputs = [0b1100_0101,
                     0b0100_0001, 
                     0b0110_0010, 
                     0b1000_0011,
                     0b1010_0100, 
                     0b0010_0000]

    # used to calibrate ADC readings to degree C
    adc_910 =  10_118_174               # ADC reading for 920 Ohm
    adc_429 =   4_771_132               # ADC reading for 429 Ohm

    for sensor in range(0,6):

        # enable channel 0 to read the desired sensor's inputs
        msg = [address_ch0 + write*64, 0b1000_0000, sensor_inputs[sensor]]
        spi.xfer2(msg)

        # read the status register
        msg = [address_status + read*64, 0]
        status_result = spi.xfer2(msg)

        # keep reading the status register until there is new data 
        # (i.e. highest bit=0)
        while status_result[1] > 0b0111_111:
            status_result = spi.xfer2(msg)

        # read the new adc measurement
        msg = [address_data + read*64, 0, 0, 0]
        data_result = spi.xfer2(msg)

        # convert the 24 bit adc reading into a decimal value
        decimal_result = data_result[1]*(2**16) + data_result[2]*(2**8) + data_result[3]

        # Determine resistance for the sensor reading
        resistance = 91.02 + (42.94 - 91.02) * (decimal_result - adc_910) / (adc_429 - adc_910)

        # Convert resistance to temperature via interp function from
        # previously opened file convert_resistance_to_termperature.py,
        # First check range(19,390) which is necessary for the function
        if resistance < 19 or resistance > 390:
            if len(new_ts[sensor]) > 1:
                print(f"ADC reading {resistance} from sensor {sensor}"
                    " not in range(19,390) \nas required by "
                    "interp_resist_to_temp."
                    f"\nPrevious value {new_ts[sensor][-1]} will be "
                    "repeated.")
                temperatures[sensor] = new_ts[sensor][-1]

            else:
                print(f"The 1st ADC reading of {resistance} from sensor"
                    f" {sensor} not in range(19,390) \nas required by "
                    "interp_resist_to_temp.\n0 will be assigned")
                temperatures[sensor] = 0

        else:
            temperatures[sensor] = interp_resist_to_temp(resistance)

    return temperatures


def read_pressure():
    def read_resp():
#        global pg
        resp = pg.read_until(b'\r')
        return str(resp.strip(b'\r').decode('utf-8'))

    global pg

    pg.write(b'STREAM_ON\r')
    pg.flushInput()
    pressure = 0
    resp = read_resp().split(' ')
    pressure += float(resp[0].split(',')[0])
    pg.write(b'STREAM_OFF\r')
    pg.flushInput()
#    print(f"Pressure = {pressure}")
    return pressure

####################################################################
# Open files to initialize sensors or convert resistance to temperature
####################################################################

# open file that converts resistance to temperature
with open("convert_resistance_to_temperature.py") as convert_r:
    exec(convert_r.read())

# initialize CDC registers to measure levels
with open("init_cdc.py") as init_l:
    exec(init_l.read())

# initialize ADC registers to measure temperatures
with open("init_temperature_registers.py") as init_t:
    exec(init_t.read())

# pg is a set of functions used to communicate with the pressure gauge
# with arguments: (port, baudrate, # data bits,parity=none, stop bits)
pg = serial.Serial('/dev/ttyUSB0', 9600, 8, 'N', 1, timeout=1)

# initialize pressure gauge
with open("init_pressure.py") as init_p:
    exec(init_p.read())

######################################################################
# set global variables
######################################################################

# sensors
level = 0
tempers = []
t_labels = ["t_cryo_bottom","t_under_bucket","t_sensor1", "t_sensor2",
            "t_sensor3","t_top_plate"]
run = 0

# The following variables are needed to push data into Influxdb, the 
# database on labpix used to feed grafana
bucket = "cryostat-sensors"
org = "lbl-neutrino"
token = "-IkZYxHAAahMAM_11tBbmtxr3tKpF7gC4wMlRZgw2rW6Fm-Ifykrt8ZgOo3c_h2jUYD3hNSp5FHr_IqtuXlCgw=="
url = "http://labpix.dhcp.lbl.gov:8086"

######################################################################
# main
######################################################################

# sign into and set up Influxbd for pushing data
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

while(run == 0):

    # get new level value from cdc
    level = read_cdc()  # read a new value from cdc

    # write level to influxDB
    p = influxdb_client.Point("larpix_slow_controls").field("level", level)
    write_api.write(bucket=bucket, org=org, record=p)

    # get 6 new temperature values from adc
    tempers = read_adc()

    # write temperatures to influxdb
    for i in range(0,6):
        p = influxdb_client.Point("larpix_slow_controls").field(t_labels[i], tempers[i])
        write_api.write(bucket=bucket, org=org, record=p)

    # read pressure
    pressure = read_pressure()
    # write level to influxDB
    p = influxdb_client.Point("larpix_slow_controls").field("pressure", pressure)
    write_api.write(bucket=bucket, org=org, record=p)
