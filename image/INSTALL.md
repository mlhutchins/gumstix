Installing and Creating a new Gumstix microSD Card
========

The Gumstix images are made with Bitbake and Yocto, with instructions found at: https://github.com/gumstix/Gumstix-YoctoProject-Repo

1. Format microSD card with mk2partsd

Make sure the microSD in located at /dev/sdb!

sudo mk2partsd /dev/sdb 

2. Run these commands to install a new image to a formatted microSD card in /dev/sdb

cp MLO u-boot.img uImage /media/boot
sudo tar xaf gumstix-xfce-image-overo.tar.bz2 -C /media/rootfs --strip-components=1
sync

3. Mount rootfs partition

4. Copy over setup and install files

cd ..
sudo cp -r firstRunFiles serial user_manual image /media/rootfs/home/root/
sync

5. Setup networking

NET=/media/rootfs/etc/network/interfaces

sudo cp $NET ${NET}.defaults
sudo cp firstRunFiles/interfaces $NET

# Disable NetworkManager
sudo rm /media/rootfs/etc/systemd/system/multi-user.target.wants/NetworkManager.service

6. Unount and eject microSD card

7. Boot on Gumstix

8. Run (via root) firstRunFiles/install.sh and firstRunFiles/setup.sh
