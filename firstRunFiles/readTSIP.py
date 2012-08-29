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

#ser.open()
#ser.isOpen()

while True:
	time.sleep(0.25)
	line=ser.read(ser.inWaiting())
	if (len(line) > 0 ):
		print line.encode('hex')
		hexline=line.encode('hex')
		start=hexline.find('108fab')
		end=hexline.find('1003')
		primTiming=hexline[start+6:end]
		start=hexline.find('108fac')
		end=hexline.find('1003',start)
		secTiming=hexline[start+6:end]
		
		fix=secTiming[12*2-2:12*2]
		hexTemp=secTiming[32*2-2:35*2]
		hexLat=secTiming[36*2-2:43*2]
		hexLong=secTiming[44*2-2:51*2]
		temp=struct.unpack('!f',hexTemp.decode('hex'))
		lat=struct.unpack('!d',hexLat.decode('hex'))
		long=struct.unpack('!d',hexLong.decode('hex'))
		pi=3.1415926535898
		temp=temp[0]
		lat=lat[0] * 180 / pi
		long = long[0] * 180 / pi
		print 'Temperature: ' + str(temp) + \
			', Latitude: ' + str(lat) + \
			', Longitude: ' + str(long)
#	print ser.read(ser.inWaiting()).encode('hex')
#	print binhex.binascii.hexlify(ser.readline(1000))
#	print ' '
