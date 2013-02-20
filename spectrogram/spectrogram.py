import scipy
import numpy

## Read in Wideband VLF Data

# Opens data file as binary file
fd = open('../../MATLAB/WB20120515175200.dat', 'rb')

# Import data as array
#	fd is filename
#	dtype is data type, currently correct version is unknown
#	count is how many lines, -1 is EOF
#	sep is delimiter, "" is for binary
time = numpy.fromfile(fd,dtype=numpy.float64,count=1,sep="")
Fs = numpy.fromfile(fd,dtype=float,count=2,sep="")
offset = numpy.fromfile(fd,dtype=float,count=3,sep="")
data = numpy.fromfile(fd,dtype=numpy.float32,count=-1,sep="")

