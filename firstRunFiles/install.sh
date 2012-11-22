# Install necessary system packages

# Comment dhclient out if setting up via SSH
echo 'Starting DHCP'
dhclient

echo 'Installing packages...'
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
opkg install apache2
# opkg install gpsd

# opkg remove dropbear --force-removal
# opkg install openssh

# Update and set clock
echo 'Setting clock'
/usr/bin/ntpdate -s -u bigben.cac.washington.edu

echo 'System update'
opkg upgrade

echo 'Run setup.sh'
