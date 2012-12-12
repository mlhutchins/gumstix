# Change Root password
echo 'Changing Root Password:'
passwd

# Setup Sferix user
echo 'Creating sferix account'
adduser sferix
usermod -s /bin/bash -G sferix sferix
usermod -a -G audio sferix
usermod -a -G dialout sferix
touch sferix_sudo
echo 'sferix ALL=(ALL) ALL' >> sferix_sudo
chmod 0440 sferix_sudo
cp sferix_sudo /etc/sudoers.d/
rm sferix_sudo

# Set user path
echo PATH=${PATH}:/home/sferix/bin > /home/sferix/.profile
echo export PATH >> /home/sferix/.profile

# Copy over configuration files
echo 'Copying Configuration Files'
DIR=''
cp ${DIR}sshd_config /etc/ssh/
#cp ${DIR}gpelogin /etc/sysconfig/
cat ${DIR}.bashrc >> /home/sferix/.profile
cp ${DIR}.bashrc ~/.profile
cp ${DIR}.vimrc ~/
cp ${DIR}.vimrc /home/sferix/
cp ${DIR}iptables /etc/iptables.rules
cp ${DIR}resolv.conf /etc/
cp ${DIR}ntp.conf /etc/
cp ${DIR}NetworkManager.conf /etc/NetworkManager/
rm /etc/rc*.d/*NetworkManager
cp ${DIR}dropbear /etc/init.d/
cp ${DIR}httpd.conf /etc/apache2/
cp ${DIR}gpsd /etc/default/

# Install toga
echo 'Installing Toga'
tar -xvf ${DIR}toga.arm.bin.tar -C /home/sferix

# Setup toga folders on ramdisk
mkdir /media/ram/public_html
mkdir /media/ram/sferics
mkdir /home/sferix/public_html_static
ln -s /media/ram/sferics /home/sferix/sferics
ln -s /media/ram/public_html /home/sferix/public_html
touch /home/sferix/sferics/sferics.log
chown -R sferix /home/sferix
chown -R sferix /home/sferix/sferics
chown -R sferix /media/ram/sferics
chown -R sferix /media/ram/public_html
chown sferix /home/sferix/sferics/sferics.log

# Create folders at startup
cp ${DIR}ramdisk.sh /etc/init.d/
ln -s /etc/init.d/ramdisk.sh /etc/rc5.d/S90ramdisk

# Set /dev/snd ownership at startup
cp ${DIR}setsnd.sh /etc/init.d/
ln -s /etc/init.d/setsnd.sh /etc/rc5.d/S90setsnd

# Install TSIP programs
mkdir /home/sferix/gps
cp ${DIR}readTSIP.py /home/sferix/gps
cp ${DIR}sendTSIP.py /home/sferix/gps
cp ${DIR}startGPSD.py /home/sferix/gps
chown -R sferix /home/sferix/gps

# Install sferix crontab
crontab -u sferix ${DIR}crontab_install

# Create gps.log file
touch /home/sferix/public_html/gps.log
chown sferix /home/sferix/public_html/gps.log

# Add flash4 into authorized keys
mkdir /home/sferix/.ssh
cp ${DIR}authorized_keys /home/sferix/.ssh
chown sferix /home/sferix/.ssh
chown sferix /home/sferix/.ssh/authorized_keys

# Link public_html to htdocs
mv /usr/share/apache2/htdocs /usr/share/apache2/htdocs.orig
ln -s /home/sferix/public_html /usr/share/apache2/htdocs
chmod a+rx /home/sferix/public_html
cp ${DIR}index.html /home/sferix/public_html_static/

# Install preamp startup scripts
echo "Installing preamp scripts"
mkdir /home/sferix/preamp
cp ${DIR}preamp* /home/sferix/preamp/
chown sferix /home/sferix/preamp
chown sferix /home/sferix/preamp/*
cp ${DIR}preamp.sh /etc/init.d/
ln -s /etc/init.d/preamp.sh /etc/rc5.d/S90preamp

echo 'Reboot recommended'

