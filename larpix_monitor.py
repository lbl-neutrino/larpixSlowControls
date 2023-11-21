####################################################################
# Monitor the temperature, level of liquid, pressure and heat supplied to 
# the larpix cryostat. Write the data to the InfluxDB database on labpix
# for monitoring by grafana
####################################################################

# used to get mean and median of ADC readings
import numpy as np

# influxDB is the database on labpix used by grafana to monitor controls
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# An SPI (Serial Peripheral Interface bus) transports information to or 
# from the AD7124-8 (temperature sensors)
import spidev
spi = spidev.SpiDev()           # abbreviate spidev

# serial is used to read/write data to the pressure gauge through the
# raspberry pi's USB port
import serial

# pyvisa contains a library of commands used to communicate with the 
# Rigol DP932U that supplies power to the heating strips. Before it 
# will work you must install pyusb, pyvisa, and pyvisa-py on the server.
import pyvisa

import time

######################################################################
# Functions
######################################################################

# Read the level of liquid in the Larpix Cryostat, by reading a CDC 
# (capacitance to digital converter). To improve precision this routine 
# reads capacitance 10 times, takes the median of every 5, and then 
# averages the medians.
def read_level():

    num_test = 10                           # number of cdc readings
    num_median = 5                          # size of the median set
    caps, median_levels = [], []
    cap, i, median_cap, level = 0,0,0,0

    # used to calibrate levels to capacitance
    sensor_length = 300
    min_cap = 1.0646713
<<<<<<< HEAD
    max_cap = 9.5106614                    # small bucket w sensor diagonal
#    max_cap = 3.6808461                   # this value for large bucket is not right
=======
#    max_cap = 9.5106614                    # small bucket w sensor diagonal
    max_cap = 3.6808461                     # large bucket w sensor vertical
>>>>>>> 1e273dd8bbb3051ed1ed21e896e9c8dde2d6b235

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
def read_tempers():

    # initialize variables
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

        # Convert resistance to temperature in Celcius (via interpolation
        # function from convert_resistance_to_termperature.py, and 
        # convert celcius to kelvin. First check range(19,390) which 
        # is necessary for the conversion function to work
        if resistance < 19 or resistance > 390:
            print(f"ADC reading {resistance} from sensor {sensor}"
                " not in range(19,390) \nas required by "
                "interp_resist_to_temp.")
            # this eroneous value is intended to alert user to a problem
            temperatures[sensor] = 100
        else:
            temperatures[sensor] = interp_resist_to_temp(resistance)

    return temperatures

# get new pressure reading
def read_pressure():
    def read_resp():
        resp = pg.read_until(b'\r')
        return str(resp.strip(b'\r').decode('utf-8'))

    # pg identifies a set of functions in the imported serial library
    # that will communicate through the pi's USB port
    global pg

    pg.write(b'STREAM_ON\r')
    pg.flushInput()
    pressure = 0
    resp = read_resp().split(' ')
    pressure += float(resp[0].split(',')[0])
    pg.write(b'STREAM_OFF\r')
    pg.flushInput()

    return pressure

# used to turn heating strips off once t>10C
def set_heat(vol, curr, on_off):

    global power_supply

    # reset the power supply
    power_supply.write('*RST')
    time.sleep(0.5)

    power_supply.write(':INST CH1')             # identify the channel
    time.sleep(0.5)
    power_supply.write(f':CURR {curr}')         # set current level
    time.sleep(0.5)
    power_supply.write(f':VOLT {vol}')          # set voltage level
    time.sleep(0.5)
    power_supply.write(f':OUTP CH1,{on_off}')   # turn on/off channel
    time.sleep(0.5)
    power_supply.write(':INST CH2')             # repeat for channel 2
    time.sleep(0.5)
    power_supply.write(f':CURR {curr}')
    time.sleep(0.5)
    power_supply.write(f':VOLT {vol}')
    time.sleep(0.5)
    power_supply.write(f':OUTP CH2,{on_off}')

# measure the power being supplied to the heating strips
def read_heat():

    global power_supply
    power1, power2 = 0,0

    # measure power supplied to heat strip 1 and 2
    power1 = power_supply.query(':MEAS:POWE? CH1')
    power1 = float(str(power1.strip('\n\r')))

    power2 = power_supply.query(':MEAS:POWE? CH2')
    power2 = float(str(power2.strip('\n\r')))

    return power1, power2
    
####################################################################
# Open files to initialize sensors or convert resistance to temperature
####################################################################

# open file that converts resistance to temperature
with open("convert_resistance_to_temperature.py") as convert_r:
    exec(convert_r.read())

# initialize CDC registers to measure liquid level
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

# Connect to the heating strip power supply
usb_heat = 'USB0::6833::42152::DP9C243500285::0::INSTR' # ID the port
rm = pyvisa.ResourceManager('@py')          # abreviate resource mgr
power_supply = rm.open_resource(usb_heat)   # connect to the usb port

######################################################################
# set global variables
######################################################################

# level and temperature sensors
level = 0
tempers = []
t_labels = ["t_cryo_bottom","t_under_bucket","t_sensor1", "t_sensor2",
            "t_sensor3","t_top_plate"]
run = 0

# power supplied to the heating strips
heat1, heat2 = 0,0

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
    level = read_level()  # read a new value from cdc

    # send level to influxDB
    p = influxdb_client.Point("larpix_slow_controls").field("level", level)
    write_api.write(bucket=bucket, org=org, record=p)

    # get 6 new temperature values from adc
    tempers = read_tempers()

    # send temperatures to influxdb
    for i in range(0,6):
        p = influxdb_client.Point("larpix_slow_controls").field(t_labels[i], tempers[i])
        write_api.write(bucket=bucket, org=org, record=p)

    # get power supplied by DP932U to heat strips
    heat1, heat2 = read_heat()
    
    # if the temperature at the bottom of the cryostat (tempers[0])
    # gets above 0K, wait 5s, test again, if still > 0K (i.e. 
    # not an eroneous reading) then turn off heating strips
    if ((heat1 or heat2) > 1) and (tempers[2] > 0): 
        time.sleep(5)
        if tempers[2] > 0:
            set_heat(0,0,0)
            heat1, heat2 = read_heat()

    # send power supplied to heat strips into influxdb
    p = influxdb_client.Point("larpix_slow_controls").field("heat_power1", heat1)
    write_api.write(bucket=bucket, org=org, record=p)
    p = influxdb_client.Point("larpix_slow_controls").field("heat_power2", heat2)
    write_api.write(bucket=bucket, org=org, record=p)

    # read pressure
    pressure = read_pressure()
    # write pressure to influxDB
    p = influxdb_client.Point("larpix_slow_controls").field("pressure", pressure)
    write_api.write(bucket=bucket, org=org, record=p)
