import scipy
import numpy
from bitstring import BitArray, BitStream

## Read in Wideband VLF Data

# Opens data file as binary file
fd = open('../../MATLAB/WBTest.dat', 'rb')
f = BitStream(fd)
# Import data as array
#	fd is filename
#	dtype is data type, currently correct version is unknown
#	count is how many lines, -1 is EOF
#	sep is delimiter, "" is for binary

time = f.read(32).intle
Fs = f.read(64).floatle
offset = f.read(64).floatle

#time = numpy.fromfile(fd,dtype=numpy.float64,count=1,sep="")
#Fs = numpy.fromfile(fd,dtype=float,count=2,sep="")
#offset = numpy.fromfile(fd,dtype=float,count=3,sep="")
#data = numpy.fromfile(fd,dtype=numpy.float32,count=-1,sep="")

