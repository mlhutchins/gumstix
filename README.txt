This is the collection of scripts, settings, and installation files for creating the current Angstrom OS for a World Wide Lightning Location Network (WWLLN) Service Unit.

The WWLLN location programs need to be decrypted from toga.arm.bin.tar.gpg with the password provided by the WWLLN management team. Or the files can be requested directly. Place the decrypted files (as a .tar file) in the same directory as the .gpg file (firstRunFiles).

To create a working OS use a microSD card of at least 8GB and run the makeSD.sh script after altering it to point to the unmounted card location. This script has only been tested on Ubuntu running in a Virtual Machine.

Once the card has been created run it from a Gumstix WaterSTORM COM with a Tobi breakout board. It will take about an hour or two to configure the kernal and all of the modules. Once configured boot and run the install.sh followed by the setup.sh scripts from the root account.

If you are running a previous version of the Service Unit software you can run the upgrade scripts to get to the most up to date version. The file ~/version.txt in the host home directory will give the current OS version. The scripts need to be run sequentially as there is currently no compiled set of patches.
