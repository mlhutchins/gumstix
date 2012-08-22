# Install necessary system packages

# Comment dhclient out if setting up via SSH
echo 'Starting DHCP'
dhclient

echo 'Installing packages...'
opkg update
opkg install gcc
opkg install libstdc++6
opkg install gd
opkg install ntp
opkg install ntp-bin
opkg install vim
opkg install iptables
# opkg install gpsd

# opkg remove dropbear --force-removal
# opkg install openssh

# Update and set clock
echo 'Setting clock'
/usr/bin/ntpdate -s -u bigben.cac.washington.edu

echo 'Run setup.sh'
