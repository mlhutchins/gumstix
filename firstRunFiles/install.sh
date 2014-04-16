# Install necessary system packages

# Comment dhclient out if setting up via SSH
echo 'Starting DHCP'
dhclient

echo 'Installing packages...'
smart update
smart install ntp-utils ntpdate

echo 'Upgrading All System Software...'
smart upgrade

# Update and set clock
echo 'Setting clock'
/usr/bin/ntpdate -s -u bigben.cac.washington.edu

echo 'Run setup.sh'
