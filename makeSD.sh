# Make and populate Gumstix microSD card for WWLLN

# Copy necessary files from ~/bbImages to ~/Work/ and rename
#cp ~/bbImages/MLO-overo ~/Work/bitbake/MLO
# Use updated MLO instead
#cp ~/Work/Angstrom/mlo-updated ~/Work/bitbake/MLO
#cp ~/bbImages/uImage-overo.bin ~/Work/bitbake/uImage
#cp ~/bbImages/u-boot-overo.bin ~/Work/bitbake/u-boot.bin
#cp ~/Work/Angstrom/uImage ~/Work/bitbake/uImage
#cp ~/Work/Angstrom/u-boot.bin ~/Work/bitbake/u-boot.bin
#cp ~/bbImages/omap3-console-image-overo.tar.bz2 ~/Work/bitbake/rootfs.tar.bz2

# Card size in bytes /255 /63 /512 to rounded down to get cylinders
IMG=sakoman-gnome-image.tar.bz2
UIMAGE=uImage-3.0-r102-omap3-multi.bin
SD=/dev/sdb
DIR=~/gumstix/baseKernel/
MOD=modules-3.0-r102-omap3-multi.tgz

echo Loading ${DIR}${IMG} onto $SD

echo 'Creating Parition Table'
# Partition the card
dd if=/dev/zero of=$SD bs=1024 count=1024

# Count Cylinders
SIZE=`fdisk -l $SD | grep Disk | awk '{print $5}'` 
echo DISK SIZE - $SIZE bytes
CYL=`echo $SIZE/255/63/512 | bc`
echo CYLINDERS - $CYL

# Make partition table
{
echo 128,130944,0x0C,*
echo 131072,,,-
} | sfdisk --force -D -uS -H 255 -S 63 -C $CYL $SD

echo 'Waiting for partition to settle'
sleep 1
echo '.'
sleep 3
echo '..'
sleep 3
echo '...'
sleep 3


echo 'Formatting and Mounting'
#Format and Mount
mkfs.vfat -F 32 ${SD}1 -n boot
mke2fs -j -L rootfs ${SD}2
sleep 2
rm -r /media/boot
rm -r /media/rootfs
sleep 1
mkdir /media/boot
mkdir /media/rootfs
sleep 1
mount -t vfat ${SD}1 /media/boot
mount -t ext3 ${SD}2 /media/rootfs
sleep 1

# Copy over boot files and expand OS
echo 'Copying boot files and rootfs'
cp ${DIR}MLO /media/boot/MLO
cp ${DIR}u-boot.bin /media/boot/u-boot.bin
cp $DIR$UIMAGE /media/boot/uImage
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

rmdir /media/boot
rmdir /media/rootfs

echo 'Load into Gumstix and run /home/root/firstRun.sh'
