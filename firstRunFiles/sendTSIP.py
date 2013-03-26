# Python program to send Resolution T serial TSIP messages

# Import modules
import serial
import time
import binhex
import struct
import os
import sys


gpsd = os.popen('ps ax | grep gpsd').read()
if '/dev/ttyO0' in gpsd:
        gpsd_check = raw_input('Terminate GPSD? (y/n)')
        if 'y' in gpsd_check:
                os.system('killall gpsd')
        else:   
                sys.exit('Serial port in use by gpsd')

# Configure serial connection
ser = serial.Serial(
        port='/dev/ttyO0',
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
)

messages={'01':'101e4b1003'.decode('hex'),
		'02':'101e0e1003'.decode('hex'),
        '03':['10bb00070204ff3db2b8c2408000004140000040c00000dd01ffffffffffffffffffffffffffffffffff1003'.decode('hex'),
             '108e4e041003'.decode('hex'),
             '108e20001003'.decode('hex'),
             '108e21001003'.decode('hex'),
             '108e230010031035120200201003'.decode('hex')],
		'06':'107a0001000000781003'.decode('hex'),
		'07':'10bc000606030000000204001003'.decode('hex'),	
		'50':'108e261003'.decode('hex'),
		'99':'Exit'
}

#http://gregstoll.dyndns.org/~gregstoll/floattohex/

while True:
	print 'This program allows sending of prerecorded TSIP messages'
	print 'Enter the message number to send:'
	print '		01 - Reset GPS (Hard)'
	print '		02 - Reset GPS (Warm)'
	print '		03 - Configre GPS'	
	print '		06 - Set NMEA Settings'
	print '		07 - Switch to NMEA'
	print '		50 - Write Configuration to ROM'
	print '		raw - Custom message'
	print '		99 - Exit'	


	result=raw_input('Message number:')
	if result in '99':
		break
	elif result in 'raw':
		raw=raw_input('Message:')
		print 'Writing: ' + str(raw.decode('hex').encode('hex'))
		ser.write(raw.decode('hex'))
	elif result in '03':
		for bin in messages[result]:
			print 'Writing: ' + str(bin.decode('hex').encode('hex'))
			ser.write(bin)
	elif result in '07':
		print '	Switching to NMEA can only be reversed by a manual power cycle.'
		confirm = raw_input('	Continue (y/n)?')
		if confirm in 'y':
			ser.write(messages[result])
	else:
		ser.write(messages[result])



