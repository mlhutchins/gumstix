# Check to see if readTSIP or sendTSIP is running

import os

gpsd_command = 'gpsd -b -n /dev/ttyO0'

gpsd = os.popen('ps ax | grep gpsd').read()

gpsd_check = gpsd_command in gpsd

tsip = os.popen('ps ax | grep TSIP').read()

tsip_check = 'readTSIP.py' in tsip or 'sendTSIP.pu' in tsip

if not tsip_check and not gpsd_check:
	os.system(gpsd_command)

