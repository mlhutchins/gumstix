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

# Allow anyone to access sound
chmod -R a+rwX /dev/snd
chmod -R a+rwX /dev/dsp

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
*cp ${DIR}NetworkManager.conf /etc/NetworkManager/
rm /etc/rc*.d/*NetworkManager
cp ${DIR}dropbear /etc/init.d/
cp ${DIR}httpd.conf /etc/apache2/
cp ${DIR}gpsd /etc/default/

# Install toga
echo 'Installing Toga'
tar -xvf ${DIR}toga.arm.bin.tar -C /home/sferix
mkdir /home/sferix/public_html
chown -R sferix /home/sferix
cp ${DIR}readTSIP.py /home/sferix/bin

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
cp ${DIR}index.html /home/sferix/public_html/

echo 'Reboot recommended'

