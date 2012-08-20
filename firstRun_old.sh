#Update packages necessary for toga

# Comment dhclient out if setting up via SSH
#dhclient
echo 'Installing packages...'
opkg update
opkg install gcc
opkg install libstdc++6
opkg install gd
opkg install ntp
opkg install ntp-bin
opkg install vim
opkg install iptables
opkg install gpsd

opkg remove dropbear --force-removal-of-dependent-packages
opkg install openssh

# Update and set clock
echo 'Setting clock'
/usr/bin/ntpdate -s -u bigben.cac.washington.edu

# Change Root password
echo 'Changing Root Password:'
passwd

# Setup Sferix user
echo 'Creating sferix account'
adduser sferix
usermod -s /bin/bash -G sferix sferix
usermod -a -G audio sferix
#echo 'Changing Sferix Password:'
#passwd sferix
echo 'sferix ALL=(ALL) ALL' >> /etc/sudoers
chmod 440 /etc/sudoers

# Allow anyone to access sound
chmod -R a+rwX /dev/snd
chmod -R a+rwX /dev/dsp

# Set user path
echo PATH=$PATH > /home/sferix/.profile
echo export PATH >> /home/sferix/.profile

# Copy over configuration files
echo 'Copying Configuration Files'
DIR=firstRunFiles
cp ${DIR}/sshd_config /etc/ssh/
#cp ${DIR}/gpelogin /etc/sysconfig/
cat ${DIR}/.bashrc >> /home/sferix/.profile
cp ${DIR}/.bashrc ~/.profile
cp ${DIR}/.vimrc ~/
cp ${DIR}/.vimrc /home/sferix/
cp ${DIR}/iptables /etc/iptables.rules
cp ${DIR}/resolv.conf /etc/
cp ${DIR}/ntp.conf /etc/

# Install toga
echo 'Installing Toga'
tar -xvf ${DIR}/toga.arm.bin.tar -C /home/sferix
mkdir /home/sferix/public_html
chown -R sferix /home/sferix


echo 'Reboot recommended'

