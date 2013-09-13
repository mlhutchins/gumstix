# Python program to configure Resolution T GPS units
#
# Written by: Michael Hutchins

# Import modules
from tsip import *

serialPort = '/dev/ttyO0'

kill_gpsd(serialPort)

# Configure serial connection
ser = setup_serial(serialPort)

# Messages to send
messages={'01':['101e4b1003'.decode('hex')], # Hard Reset
		'02':['101e0e1003'.decode('hex')], # Warm Reset
        '03':['10bb00070204ff3db2b8c2408000004140000040c00000dd01ffffffffffffffffffffffffffffffffff1003'.decode('hex'), # General settings: O-D clock mode, stationary, 5 deg elev mask, dpgs auto off, datum wgs-84, anti-jamming
             '108e4e041003'.decode('hex'), # Set PPS to need >= 3 satellites
			 '108ea2a01003'.decode('hex'), # Set time reporting to UTC
			 '108ea5004500001003'.decode('hex')], # Set auto event packet mask (enable number of satellites)
		'07':['107a0001000000011003'.decode('hex'), #Set NMEA settings
			  '10bc000606030000000204001003'.decode('hex')], #Switch to NMEA messages (4800 8N1)
		'50':['108e261003'.decode('hex')], # Write to ROM
		'99':'Exit'
}

#http://gregstoll.dyndns.org/~gregstoll/floattohex/

for bin in messages['03']:
		print 'Writing: ' + str(bin.encode('hex'))
		ser.write(bin)
		time.sleep(0.15)
