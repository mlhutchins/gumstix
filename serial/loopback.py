from tsip import *

serialPort = '/dev/tty.usbserial-A5012UO4'

ser = setup_serial(serialPort)

while True:
	
	line = ser.read(ser.inWaiting())
	print 'Raw Receive :' + str(line)
	line.encode('hex')
	print 'Received: ' + line.encode('hex')

	message = raw_input('Message: ')
	if message == 'exit':
		break
	messageHex = message.decode('hex')
	print 'Sending :' + str(messageHex)
	ser.write(messageHex)

	time.sleep(0.1)
