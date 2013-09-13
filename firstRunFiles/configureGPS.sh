#!/bin/sh
#
# Sets GPS configuration on startup
#

start(){
	echo -n "Setting GPS configuration"
	python /home/root/gps/Configuration.py
}
stop(){
	echo -n "Nothing done."
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
