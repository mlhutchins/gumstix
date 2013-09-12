echo 'Starting 1.5 to 1.6 upgrade...'
cp version.txt /home/sferix/
cp version.txt /home/host/

echo 'Updated TSIP routines'
cp tsip.py /home/sferix/gps/
cp tsip.py /home/host/gps/
rm /home/sferix/gps/startGPSD.py
rm /home/host/gps/startGPSD.py

echo 'Updating paths'
cp profile /home/sferix/.profile
cp profile /home/host/.profile
cp profile /home/root/.profile

echo 'Software 1.5 to 1.6 upgrade finished'
echo ' '
# Final instructions
cat post_setup.txt
