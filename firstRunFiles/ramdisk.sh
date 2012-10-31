#!/bin/sh
#
# Creates folders on the ramdisk.
#

start(){
	echo -n "Creating sferics and public_html on ramdisk."
	mkdir /media/ram/sferics
	mkdir /media/ram/public_html
	cp -r /home/sferix/public_html_static/* /media/ram/public_html/
	echo -n "Folders created."
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
