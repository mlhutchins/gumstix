import serial
import time
import binhex
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

#	print ser.read(ser.inWaiting()).encode('hex')
#	print binhex.binascii.hexlify(ser.readline(1000))
#	print ' '
