from tsip import *

serialPort = '/dev/tty.usbserial-A5012UO4'

ser = setup_serial(serialPort)

while True:
	
	line = ser.read(ser.inWaiting())
	line.encode('hex')
	print 'Received: ' + line

	message = raw_input('Message: ')
	ser.write(message)

	time.sleep(0.1)
