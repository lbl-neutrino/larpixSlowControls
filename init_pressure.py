#####################################################################
# reads pressure inside cryostat, as fed to the cryo-control pi 
# through a USB port
#####################################################################

def read_resp():
    global pg

    resp = pg.read_until(b'\r')
    return str(resp.strip(b'\r').decode('utf-8'))

global pg

# pg is a set of functions used to communicate with the pressure gauge
# via the pi's USB port. 
# Arguments: (port, baudrate, # data bits,parity=none, stop bits)
pg = serial.Serial('/dev/ttyUSB0', 9600, 8, 'N', 1, timeout=1)

# open the serial port
if not pg.is_open:
    pg.open()
pg.flushInput()

# identify and print the serial device found on the pi's usb port
pg.write(b'*IDN?\r')

# check to see if there are any errors
resp = read_resp()
if not resp:
    raise RuntimeError('No pressure signal found at pi usb port'
                       ' - IS PRESSURE GAUGE TURNED ON?')
    print('device reports fault {}'.format(resp))
