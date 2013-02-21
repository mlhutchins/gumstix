import scipy
import numpy

## Read in Wideband VLF Data

fileName = '../../../MATLAB/WBTest.dat'

fid = open(fileName, 'rb')

time = numpy.fromfile(fid, dtype=numpy.dtype('<i4'), count = 1)
Fs = numpy.fromfile(fid, dtype=numpy.dtype('<f8'), count = 1)
offset = numpy.fromfile(fid, dtype=numpy.dtype('<f8'), count = 1)
y = numpy.fromfile(fid, dtype=numpy.dtype('<i2'))
y = y[10:]
print len(y)
print y[:10]
