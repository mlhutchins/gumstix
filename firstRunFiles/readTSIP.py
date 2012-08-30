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

# List of possible alerts
alerts=[]
alertList=['Not used','Antenna Open','Antenna Shorted','Not tracking satellites',
		'Not used','Survey In Progress','No Stored Position','Leap Second Pending',
		'In Test Mode','Position is Questionable','Not Used','Almanac not complete',
		'PPS was not generated','Not used','Not used','Not used','Not used']

# Continuously monitor serial line
while True:
	
	# Wait 0.25 seconds and check messages in serial buffer
	time.sleep(0.25)
	line=ser.read(ser.inWaiting())
	if (len(line) > 0 ):
#		print line.encode('hex')

		# Extract primary and secondary timing messages
		hexline=line.encode('hex')
		start=hexline.find('108fab')
		end=hexline.find('1003')
		primTiming=hexline[start+6:end]
		start=hexline.find('108fac')
		end=hexline.find('1003',start)
		secTiming=hexline[start+6:end]

#		print primTiming
		# Check for proper length of primary timing message
		if (len(primTiming) == 34):
		
			# Select and convert date (Hex string to decimal to string)
			seconds=str(int(primTiming[10*2:10*2+2],16))
			minutes=str(int(primTiming[11*2:11*2+2],16))
			hours=str(int(primTiming[12*2:12*2+2],16))
			day=str(int(primTiming[13*2:13*2+2],16))
			month=str(int(primTiming[14*2:14*2+2],16))
			year=str(int(primTiming[15*2:],16))

			# Pad digits
			if (len(seconds)==1):
				seconds='0'+seconds
			if (len(minutes)==1):
				minutes='0'+minutes
			if (len(hours)==1):
				hours='0'+hours
			if (len(day)==1):
				day='0'+day
			if (len(month)==1):
				month='0'+month	
	
			# Print results
			print year+'/'+month+'/'+day+' '+hours+':'+minutes+':'+seconds
		else:
			print 'Primary Packet Length: ' + str(len(primTiming))
		
#		print secTiming		

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
			alarms=bin(int(secTiming[10*2:11*2+2],16))[2:]
			
			# Pad alert bytes
			if (len(alarms)<16):
				padding='0'*(16-len(alarms))
				alarms=padding+alarms
				
			# Select current alerts
			alerts[:]=[];
			for i in range(0,16):
				if alarms[15-i]=='1':
					alerts.append(alertList[i])

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
	
			# Print alerts, if any
			if (len(alerts)>0):
				print 'Current Alerts: ' + alerts
		else:
			# Offset time if messages are being read partway through
			time.sleep(0.17)
			print 'Secondary Packet Length: ' + str(len(secTiming))
