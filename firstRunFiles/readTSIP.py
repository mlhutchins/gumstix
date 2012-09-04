# Python program to read Resolution T serial TSIP messages

# Import modules
import serial
import time
import binhex
import struct
import os

# Configure serial connection
ser = serial.Serial(
	port='/dev/ttyO0',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)

# Open log file
filepath='/home/sferix/public_html/gps.log'
fid = open(filepath,'a')

# List of possible alerts
alerts=[]
alertList=['Not used','Antenna open','Antenna shorted','Not tracking satellites',
		'Not used','Survey in progress','No stored position','Leap second pending',
		'In test mode','Position is questionable','Not used','Almanac not complete',
		'PPS was not generated']

# GPS Status
gpsStatus={'00':'Locked',
		'01':'Dont have GPS time',
		'03':'PDOP is too high',
		'08':'No usable satallites',
		'09':'1 Satellite',
		'0a':'2 Satellites',
		'0b':'3 Satellites',
		'0c':'The chosen sat in unusable',
		'10':'TRAIM rejected the fix'}
	# Status 00 is originally 'Doing fixes' in TSIP documentation

# Timing Flag
timingFlags={'00':'GPS Time',
		'01':'UTC Time',
		'10':'GPS PPS',
		'11':'UTC PPS',
		'20':'Time is set',
		'21':'Time is not set',
		'30':'Have UTC info',
		'31':'No UTC info',
		'40':'Time from GPS',
		'41':'Time from user'}


# Function to remove '1010' code (TSIP '10' is an escape byte)
def removeEscape(message):
	removeIndex=[]
        # Find '1010' bytes
	index=0
	a=0
	removeIndex[:]=[]
	while a>-1:
		a=message.find('1010',index)
		if a>-1:
			removeIndex.append(a)
		index=a+1
	removeIndex.reverse()
	
	# Remove extranous '10' byte
	if len(removeIndex)>0:
		for i in range(0,len(removeIndex)):
			if removeIndex[i]%2==0:
				message=message[:removeIndex[i]] + message[removeIndex[i]+2:]
	return message


# Initialize variables
removeIndex=[]
timeIndex=0


# Continuously monitor serial line
while True:
	
	# Wait 0.25 seconds and check messages in serial buffer
	time.sleep(0.25)
	timeIndex=timeIndex+0.25

	currentTime = time.localtime()
	
	if (timeIndex==0.5):
		ser.write('10271003'.decode('hex'))
		ser.write('10241003'.decode('hex'))
		line=[]
	elif (timeIndex==1.0):
		line=ser.read(ser.inWaiting())
		timeIndex=0
	else:
		line=[]	

	if (len(line) > 0 ):
#		print 'Main hexline: ' + line.encode('hex')

		# Read serial buffer
                hexline=line.encode('hex')
	
		# Extract primary and secondary timing messages
		start=hexline.find('108fab')
		end=hexline.find('1003')
		primTiming=hexline[start+6:end]
		start=hexline.find('108fac')
		end=hexline.find('1003',start)
		secTiming=hexline[start+6:end]
		start=hexline.find('1047')

                # Remove escapes
                primTiming = removeEscape(primTiming)
                secTiming = removeEscape(secTiming)

		# Extract satallite tracking information
		end=hexline.find('1003',start)
		if (start>-1):
			satLine=hexline[start+4:end]
			satLine=removeEscape(satLine)
		else:
			satLine=[]
		
		start=hexline.find('106d')
		end=hexline.find('1003',start)
		if (start>-1):
			trackline=hexline[start+4:end]
			trackline=removeEscape(trackline)
		
		# Remove escapes
		primTiming = removeEscape(primTiming)
		secTiming = removeEscape(secTiming)

#		print 'Primary Timing: ' + primTiming
#		print 'Secondary Timing: ' + secTiming

		# Check for proper length of primary timing message
		if (len(primTiming) == 32):
		
			# Select and convert date (Hex string to decimal to string)
			seconds=str(int(primTiming[10*2-2:10*2],16))
			minutes=str(int(primTiming[11*2-2:11*2],16))
			hours=str(int(primTiming[12*2-2:12*2],16))
			day=str(int(primTiming[13*2-2:13*2],16))
			month=str(int(primTiming[14*2-2:14*2],16))
			year=str(int(primTiming[15*2-2:],16))

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
	
			# Extract timing flag
			timing=bin(int(primTiming[9*2-2:9*2],16))[2:]

			# Pad timing flag
			if (len(timing)<8):
				padding='0'*(8-len(timing))
				timing=padding+timing

			# Get timing info from flags
			timingInfo=''
			for i in range(0,5):
				timingInfo = timingInfo + ', '+ timingFlags[str(i)+str(timing[7-i])]
			
			# Print results
			
			statement1 = year+'/'+month+'/'+day+' '+hours+':'+minutes+':'+seconds + ', ' + timingInfo[2:]

		else:
			time.sleep(0.07)
			statement1 = 'Primary Packet Length: ' + str(len(primTiming))
		
		# Check for proper length of secondary timing message
		if (len(secTiming) == 134):
			
			# Extract parameters of interest
			fix=secTiming[12*2-2:12*2]
			hexTemp=secTiming[32*2-2:35*2]
			hexLat=secTiming[36*2-2:43*2]
			hexLong=secTiming[44*2-2:51*2]
			alarms=bin(int(secTiming[10*2-2:11*2],16))[2:]		
	
			# Pad alert bytes
			if (len(alarms)<13):
				padding='0'*(12-len(alarms))
				alarms=padding+alarms+'0'
			
			# Select current alerts
			alerts[:]=[];
			for i in range(0,13):
				if ((alarms[i]=='1') and (alertList[i] not in 'Not used')):
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
			statement2a = 'Temperature: ' + str(temp) + \
				', Latitude: ' + str(lat) + \
				', Longitude: ' + str(long)
	
			# Print GPS Status
			statement2b = 'GPS Status: ' + gpsStatus[fix] # + ' (' + fix + ')'

			# Print alerts, if any
			if (len(alerts)>0):
				statement2c = 'Current Alerts: ' + str(alerts)[1:-1]
			else:
				statement2c=''
		else:
			# Offset time if messages are being read partway through
			time.sleep(0.07)
			statement2a = 'Secondary Packet Length: ' + str(len(secTiming))
			statement2b = ''
			statement2c = ''

		# Report the number of satellites locked and available

		if (len(trackline)>2):
			track = str(int(trackline[0],16))
		else:
			track = -1

		if (len(satLine)>2):
			sat = str(int(satLine[0:2],16))
		else:
			sat = -1

		statement3 = 'Satellites tracked: ' + track + ' (of ' + sat + ' available)'

		# Print out generated messages

		print statement1
		print statement2a
		if len(statement2b) > 0 :
			print statement2b
		if len(statement2c) > 0 :
			print statement2c
		print statement3

		# Save GPS messages every 10 minutes to log file

		if currentTime.tm_min%1 == 0 :
			fid.write(statement1 + '\n')
			fid.write(statement2a + '\n')
		        if len(statement2b) > 0 :
                        	fid.write(statement2b + '\n')  
                	if len(statement2c) > 0 :
                        	fid.write(statement2c + '\n')  
                	fid.write(statement3 + '\n')  	

			if len(open(filepath).readlines()) > 5000 :
				fid.close()
				fid = open(filepath,'r')
				log_text = fid.readlines()
				fid.close()		
				
				del log_text[0:100]
				
				fid = open(filepath,'w')
				fid.writelines(log_text)
				
				fid.close()
				
				fid = open(filepath,'a')


