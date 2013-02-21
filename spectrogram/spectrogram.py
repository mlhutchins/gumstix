import scipy
import numpy
import array

## Read in Wideband VLF Data

fileName = '../../../MATLAB/WBTest.dat'

fid = open(fileName, 'rb')

time = numpy.fromfile(fid, dtype=numpy.dtype('<i4'), count = 1)
Fs = numpy.fromfile(fid, dtype=numpy.dtype('<f8'), count = 1)
offset = numpy.fromfile(fid, dtype=numpy.dtype('<f8'), count = 1)
y = numpy.fromfile(fid, dtype=numpy.dtype('<i2'))

## Normalize to soundcard units and switch to float
y = y.astype(numpy.float)
y = y/32768

## Make the time base

t = numpy.arange(0.0,len(y))
t = t + offset
t = t/Fs


