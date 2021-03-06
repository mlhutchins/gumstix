# Python program to read Resolution T serial TSIP messages
#
# Written by: Michael Hutchins

# Import modules
from tsip import *

# Pick serial port
serialPort = '/dev/ttyO0'

# Check whether to print results to the console
print_to_console=True

if print_to_console:
	kill_gpsd(serialPort)
		
# Configure serial connection
ser = setup_serial(serialPort)

# Open log file
filepath='/home/sferix/public_html/gps.log'

# Initialize variables
removeIndex=[]
timeIndex=0

# Continuously monitor serial line
while True:
	
	# Wait 0.25 seconds and check messages in serial buffer
	time.sleep(0.25)
	timeIndex=timeIndex+0.25

	currentTime = time.localtime()
	
#	if (timeIndex==0.5):
#		ser.write('10271003'.decode('hex'))
#		ser.write('10241003'.decode('hex'))
#		line=[]
	if (timeIndex==1.0):
		line=ser.read(ser.inWaiting())
		timeIndex=0
	else:
		line=[]	

	if (len(line) > 0 ):
#		print 'Main hexline: ' + line.encode('hex')

		# Read serial buffer
		hexline=line.encode('hex')
	
		# Extract TSIP messagess
		primTiming = extractMessage('108fab',hexline)
		secTiming = extractMessage('108fac',hexline)
#		satLine = extractMessage('1047',hexline)
		trackline = extractMessage('106d',hexline)		

#		print 'Primary Timing: ' + primTiming
#		print 'Secondary Timing: ' + secTiming

		# Check for proper length of primary timing message
		if (len(primTiming) == 32):
			statement1 = printPrimary(primTiming)		
		else:
			time.sleep(0.07)
			statement1 = 'Primary Packet Length: ' + str(len(primTiming))
		
		# Check for proper length of secondary timing message
		if (len(secTiming) == 134):
			(statement2a, statement2b, statement2c) = printSecondary(secTiming)
		else:
			# Offset time if messages are being read partway through
			time.sleep(0.07)
			statement2a = 'Secondary Packet Length: ' + str(len(secTiming))
			statement2b = ''
			statement2c = ''

		# Report the number of satellites locked and available

		statement3 = printTrack(trackline)

		# Print out generated messages

		if print_to_console:
			print statement1
			print statement2a
			if len(statement2b) > 0 :
				print statement2b
			if len(statement2c) > 0 :
				print statement2c
			print statement3

		# Save GPS messages every 10 minutes to log file

		if currentTime.tm_min%10 == 0 and currentTime.tm_sec < 10:
			fid = open(filepath,'a')
			fid.write(statement1 + '\n')
			fid.write(statement2a + '\n')
		        if len(statement2b) > 0 :
                        	fid.write(statement2b + '\n')  
                	if len(statement2c) > 0 :
                        	fid.write(statement2c + '\n')  
                	fid.write(statement3 + '\n')  	

			if len(open(filepath).readlines()) > 30000 :
				fid.close()
				fid = open(filepath,'r')
				log_text = fid.readlines()
				fid.close()		
				
				del log_text[0:500]
				
				fid = open(filepath,'w')
				fid.writelines(log_text)
				
				fid.close()
				
				fid = open(filepath,'a')

			fid.close()
