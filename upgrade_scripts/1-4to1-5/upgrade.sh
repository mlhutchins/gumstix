echo 'Starting 1.4 to 1.5 upgrade...'
echo 'Removing outdate opgk repository'
# Remove out of date opkg repository
rm /etc/opkg/angstrom-base.conf

echo 'Setting sample vlf image to static website'
# Copy vlf_sample.png to public_html_static as default
cp vlf_sample.png /home/sferix/public_html_static/vlf.png

echo 'Setting gpsd to start as root (replacing root/sferix crontabs)'
# Set GPSD to start as root
crontab -u root crontab_install_root
crontab -u sferix crontab_install

echo 'Installing version.txt file'
# Install version.txt
cp version.txt /home/sferix/
cp version.txt /home/host/

echo 'Setting terminal desktop alias'
# Install terminal desktop icon
cp -r Desktop /home/sferix/
cp -r Desktop /home/host/
chown -R sferix /home/sferix/Desktop
chown -R host /home/host/Desktop

echo 'Updating opkg'
echo ' '
opkg update

echo 'Installing GPSD'
opkg install gpsd

echo 'Upgrading all software'
echo ' '
opkg upgrade

echo 'Software 1.4 to 1.5 upgrade finished'
echo ' '
# Final instructions
cat post_setup.txt
