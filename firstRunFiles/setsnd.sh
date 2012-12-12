#!/bin/sh
#
# Sets /dev/snd on startup
#

start(){
	echo -n "Setting /dev/snd ownership"
	chown -R sferix /dev/snd
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
