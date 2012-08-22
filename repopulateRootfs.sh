# Repopulate a rootfs

IMG=sakoman-gnome-image.tar.bz2
DIR=~/gumstix/baseKernel/
SD=/media/rootfs/
MOD=modules-3.0-r102-omap3-multi.tgz

echo Erasing content on $SD

rm -fr ${SD}*

echo Loading ${DIR}${IMG} onto rootfs

# Copy over boot files and expand OS
echo 'Copying rootfs'
tar xaf $DIR$IMG -C /media/rootfs
tar xzvf $DIR$MOD
rm -rf /media/rootfs/lib/modules
rm -rf /media/rootfs/lib/firmware
cp -r lib/modules lib/firmware /media/rootfs/lib/
rm -rf lib
sync

# Adjust Network and opkg parameters
echo 'Adjusting parameters'
echo 'src/gz angstrom-base http://feeds.angstrom-distribution.org/feeds/core/ipk/eglibc/armv7a/base' > /media/rootfs/etc/opkg/angstrom-base.conf
NET=/media/rootfs/etc/network/interfaces

cp $NET ${NET}.defaults
cp firstRunFiles/interfaces $NET

# Copy first run script and files
echo 'Copying firstRun script and files'
# cp firstRun.sh /media/rootfs/home/root/
cp -r firstRunFiles /media/rootfs/home/root/

# Unmount
echo 'Unmounting microSD card'
umount /media/boot
umount /media/rootfs

rmdir /media/{boot,rootfs}

echo 'Load into Gumstix and run /home/root/firstRun.sh'
