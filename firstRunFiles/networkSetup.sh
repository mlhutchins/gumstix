IP=128.208.22.30
GATEWAY=128.208.22.100
NETMASK=255.255.255.0 

sleep 60
ifconfig eth0 down
ifconfig eth0 $IP netmask $NETMASK up
route add default gw $GATEWAY
