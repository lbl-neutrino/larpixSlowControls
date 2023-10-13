def read_resp():

        global pg

        resp = pg.read_until(b'\r')
        return str(resp.strip(b'\r').decode('utf-8'))

        
global pg

pg = serial.Serial('/dev/ttyUSB0', 9600, 8, 'N', 1, timeout=1)

if not pg.is_open:
    pg.open()
pg.flushInput()

pg.write(b'*IDN?\r')
resp = read_resp()
if resp:
    print('serial device {} found'.format(resp))
else:
    raise RuntimeError('serial device could not be found!')

pg.write(b'FAULT?\r')
resp = read_resp()
if resp:
    print('device reports fault {}'.format(resp))
pg.write(b'*CLS\r')

#pg.write(b'HC_AUTO_OFF\r')

