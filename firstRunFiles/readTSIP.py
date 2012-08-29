# Python program to read Resolution T serial TSIP messages

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

# Continuously monitor serial line
while True:
	
	# Wait 0.25 seconds and check messages in serial buffer
	time.sleep(0.25)
	line=ser.read(ser.inWaiting())
	if (len(line) > 0 ):
		print line.encode('hex')

		# Extract primary and secondary timing messages
		hexline=line.encode('hex')
		start=hexline.find('108fab')
		end=hexline.find('1003')
		primTiming=hexline[start+6:end]
		start=hexline.find('108fac')
		end=hexline.find('1003',start)
		secTiming=hexline[start+6:end]
		
		# Check for proper length of secondary timing message
		if (len(secTiming) > 130):
			
			# Pad message if reserved byte gets dropped
			if (len(secTiming)==134):
				secTiming=secTiming[:24*2] + '00' + secTiming[24*2:]	

			# Extract parameters of interest
			fix=secTiming[12*2-2:12*2]
			hexTemp=secTiming[32*2:35*2+2]
			hexLat=secTiming[36*2:43*2+2]
			hexLong=secTiming[44*2:51*2+2]

			# Convert from hex to floating point decimal
			temp=struct.unpack('!f',hexTemp.decode('hex'))
			lat=struct.unpack('!d',hexLat.decode('hex'))
			long=struct.unpack('!d',hexLong.decode('hex'))
			
			# Convert from radians to degrees, pi is value hardcoded by Trimble
			pi=3.1415926535898
			temp=temp[0]
			lat=lat[0] * 180 / pi
			long = long[0] * 180 / pi

			# Print results
			print 'Temperature: ' + str(temp) + \
				', Latitude: ' + str(lat) + \
				', Longitude: ' + str(long)
		else:
			# Offset time if messages are being read partway through
			time.sleep(0.17)
			print 'Packet Length: ' + str(len(secTiming))
