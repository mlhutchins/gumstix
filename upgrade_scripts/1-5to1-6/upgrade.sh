echo 'Starting 1.5 to 1.6 upgrade...'
cp version.txt /home/sferix/
cp version.txt /home/host/

echo 'Updated TSIP routines'
cp tsip.py /home/sferix/gps/
cp tsip.py /home/host/gps/

echo 'Software 1.5 to 1.6 upgrade finished'
echo ' '
# Final instructions
cat post_setup.txt
