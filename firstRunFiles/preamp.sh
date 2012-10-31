#!/bin/sh
#
# Turns on the preamp
#

start(){
	echo -n "Turning on preamp power."
	echo 0 > /sys/class/gpio/gpio145/value
	echo -n "Preamp on."
}
stop(){
	echo -n "Turning off preamp power."
	echo 1 > /sys/class/gpio/gpio145/value
	echo -n "Preamp off."
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
