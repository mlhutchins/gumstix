# Python program to send Resolution T serial TSIP messages

# Import modules
import serial
import time
import binhex
import struct

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
		'03':'10bbff07ff04ff3f74d474408000004140000040c00000ff01ffffffffff1003'.decode('hex'),
		'04':'108e4e031003'.decode('hex'),
		'05':'108ea2001003'.decode('hex'),
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
	print '		03 - Set GPS Primary Configuration'	
	print '		04 - Set GPS PSS Configuration'
	print '		05 - Set GPS to GPS timing'
	print '		06 - Set NMEA Settings'
	print '		07 - Switch to NMEA'
	print '		50 - Write Configuration to ROM',
	print '		raw - Custom message',
	print '		99 - Exit'	


	result=raw_input('Message number:')
	if result in '99':
		break
	elif result in 'raw':
		raw=raw_input('Message:')
		ser.write(raw.decode('hex'))
	elif result in '07':
		print '	Switching to NMEA can only be reversed by a manual power cycle.'
		confirm = raw_input('	Continue (y/n)?')
		if confirm in 'y':
			ser.write(messages[result])
	else:
		ser.write(messages[result])



