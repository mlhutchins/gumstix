# Install necessary system packages

# Comment dhclient out if setting up via SSH
echo 'Starting DHCP'
dhclient

echo 'Installing packages...'
opkg update
opkg install gpsd

# Update package repository
echo 'src/gz angstrom-base http://feeds.angstrom-distribution.org/feeds/core/ipk/eglibc/armv7a/base' > /media/rootfs/etc/opkg/angstrom-base.conf

opkg update
opkg install gcc
opkg install libstdc++6
opkg install python-pyserial
opkg install gd
opkg install ntp
opkg install ntp-bin
opkg install gps-utils
opkg install vim
opkg install iptables
opkg install openvpn
opkg install vpnc
opkg remove apache2
opkg install apache2
opkg install openssh-keygen
opkg install openssh-ssh

# Update and set clock
echo 'Setting clock'
/usr/bin/ntpdate -s -u bigben.cac.washington.edu

echo 'Run setup.sh'
