#####################################################################
# set up the means to communicate with the Capacitance to Digital 
# Converter (CDC: AD7746) used to monitor the level of liquid in the
# cryostat. Configure the CDC for our purposes.
#####################################################################
import time
import smbus

# establish communication with the CDC
i2c_ch = 1
i2c_addr = 0x48
bus = smbus.SMBus(i2c_ch)
time.sleep(1)

# configure the CDC for our purposes (if these settings change you may need to recalibrate the sensor)
bus.write_byte_data(i2c_addr,0x8,0x01) # temperature config
bus.write_byte_data(i2c_addr,0x7,0x80) # Capacitance setup
bus.write_byte_data(i2c_addr,0x9,0x18) # high swing exca setup
#bus.write_byte_data(i2c_addr,0xb,0x96) # offset
bus.write_byte_data(i2c_addr,0xd,0xff) # Not needed, but changes would require recalibration
bus.write_byte_data(i2c_addr,0xb,0x7F) # offset
bus.write_byte_data(i2c_addr,0xa,0x39) # ADC config, continuous conversion mode

