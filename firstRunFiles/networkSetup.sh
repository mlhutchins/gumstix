IP=128.208.22.30
GATEWAY=128.208.22.100
NETMASK=255.255.255.0 

echo "Switch to main ethernet in 60 seconds"

sleep 30

echo "30 seconds"

sleep 20

echo "10 seconds"

sleep 10

ifconfig eth0 down
ifconfig eth0 $IP netmask $NETMASK up
route add default gw $GATEWAY
