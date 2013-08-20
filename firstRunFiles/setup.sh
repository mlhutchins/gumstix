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

# Setup Host Account
echo 'Creating host account'
adduser host
touch host_sudo
echo 'host ALL=(ALL) ALL' >> host_sudo
chmod 0440 host_sudo
cp host_sudo /etc/sudoers.d/
rm host_sudo

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
cp ${DIR}.vimrc /home/host/
cp ${DIR}iptables /etc/iptables.rules
cp ${DIR}resolv.conf /etc/
cp ${DIR}ntp.conf /etc/
cp ${DIR}NetworkManager.conf /etc/NetworkManager/
rm /etc/rc*.d/*NetworkManager
cp ${DIR}dropbear /etc/init.d/
cp ${DIR}httpd.conf /etc/apache2/
cp ${DIR}gpsd /etc/default/
cp ${DIR}networkSetup.sh /home/sferix/
cp ${DIR}networkSetup.sh /home/host/
cp ${DIR}asound.state /etc/
cp ${DIR}asound.state /home/sferix/asound.state.default
cp ${DIR}asound.txt /home/sferix/asound.txt
cp ${DIR}asound.state /home/host/asound.state.default
cp ${DIR}asound.txt /home/host/asound.txt
cp ${DIR}ntpd /etc/init.d/
cp ${DIR}hostname /etc/

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

# Set host access to public_html_static
chmod a+w /home/sferix/public_html_static
ln -s /home/sferix/public_html_static /home/host/public_html_static

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
cp ${DIR}tsip.py /home/sferix/gps
cp ${DIR}startGPSD.py /home/sferix/gps
chown -R sferix /home/sferix/gps

mkdir /home/host/gps
cp ${DIR}readTSIP.py /home/host/gps
#cp ${DIR}sendTSIP.py /home/host/gps
cp ${DIR}tsip.py /home/host/gps
cp ${DIR}startGPSD.py /home/host/gps
chown -R host /home/host/gps

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

# Install preamp scripts for host
mkdir /home/host/preamp
cp ${DIR}preamp* /home/host/preamp/
chown host /home/host/preamp
chown host /home/host/preamp/*


# Setup wideband and R-files folders
mkdir /home/sferix/R-files
chown sferix /home/sferix/R-files
mkdir /home/sferix/wideband
chown sferix /home/sferix/wideband

# Install VIM syntax file
tar -zxvf ${DIR}syntax.tar.gz
cp -r ${DIR}syntax /usr/share/vim/vim72/

# Set timezone to UTC
cp /usr/share/zoneinfo/UTC /etc/localtime

echo 'Reboot recommended'

