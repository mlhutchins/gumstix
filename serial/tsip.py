# Python module for reading/writing TSIP message to the serial port

# Import modules
import serial
import time
import binhex
import struct
import os
import sys

# If gpsd is currently using serialPort, kill gpsd
def kill_gpsd(serialPort):
	gpsd = os.popen('ps ax | grep gpsd').read()
	if serialPort in gpsd:
		gpsd_check = raw_input('Terminate GPSD? (y/n)')
		if 'y' in gpsd_check:
			os.system('killall gpsd')
		else:
			sys.exit('Serial port in use by gpsd')
		
# Open up serialPort, return handle ser
def setup_serial(serialPort):
	ser = serial.Serial(
		port=serialPort,
		baudrate=9600,
		parity=serial.PARITY_ODD,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS
	)
	return ser

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

def extractMessage(idpacket,hexline):
	start=hexline.find(idpacket)
	if start>-1:
        	end=hexline.find('1003',start)
                packet = hexline[start+len(idpacket):end]
                packet = removeEscape(packet)
	else:
		packet = str(-1)
	return packet

			
def printPrimary(primTiming):


	# Define timing flags
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
	statement1 = year+'/'+month+'/'+day+' '+hours+':'+minutes+':'+seconds # + ', ' + timingInfo[2:]
	return statement1


def printSecondary(secTiming):

	# Define GPS Status Flags
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
	
	# Define GPS Alert Status
	alerts=[]
	alertList=['Not used','Antenna open','Antenna shorted','Not tracking satellites',
		'Not used','Survey in progress','No stored position','Leap second pending',
		'In test mode','Position is questionable','Not used','Almanac not complete',
		'PPS was not generated']

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
	alarmLength = len(alarms) 
	for i in range(alarmLength):
		if ((alarms[alarmLength - i - 1]=='1') and (alertList[i] not in 'Not used')):
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
	statement2a = 'Latitude: ' + str(lat) + \
		', Longitude: ' + str(long) + \
		', Temperature: ' + str(temp)
		
	# Print GPS Status
	statement2b = 'GPS Status: ' + gpsStatus[fix] # + ' (' + fix + ')'

	# Print alerts, if any
	if (len(alerts)>0):
		statement2c = 'Current Alerts: ' + str(alerts)[1:-1]
	else:
		statement2c = ''

	return (statement2a, statement2b, statement2c)

def printTrack(trackline):
	if (len(trackline)>2):
		track = str(int(trackline[0],16))
	else:
		track = '-1'

	statement3 = 'Satellites tracked: ' + track
	return statement3

