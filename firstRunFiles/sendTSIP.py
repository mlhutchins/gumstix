# Python program to send Resolution T serial TSIP messages

# Import modules
import serial
import time
import binhex
import struct

# Configure serial connection
ser = serial.Serial(
        port='/dev/ttyO0',
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
)

