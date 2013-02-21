import scipy
import numpy
from bitstring import BitArray, BitStream

## Read in Wideband VLF Data

fileName = '../../../MATLAB/WBTest.dat'

# Opens data file as binary file
fd = open(fileName, 'rb')
f = BitStream(fd)

# Read WB data parameters
time = f.read(32).intle
Fs = f.read(64).floatle
offset = f.read(64).floatle

fd = open(fileName, 'rb')

y = numpy.fromfile(fd, dtype=numpy.dtype('<i2'))
y = y[10:]
print len(y)
print y[:10]

