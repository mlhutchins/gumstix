#!/bin/sh
#
# Forces a call to networking start
#

start(){
	echo -n "Starting Network Services."
	/etc/init.d/networking start
}
stop(){
	echo -n "No action."
}
restart(){
	stop
	start
}

case "$1" in
	start)
		start
	;;
	stop)
		stop
	;;
	restart|reload)
	restart
	;;
	*)
	echo $"Usage: $0 {start|stop|restart}"
	exit 1
esac

exit $?
