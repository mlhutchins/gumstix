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

## Spectrogram ##

Nw = 2**10 # Hanning window length
Ny = len(y) # Sample length

# Create Hanning window
j = numpy.arange(1.0,Nw+1)
w = 0.5 * (1 - numpy.cos(2*numpy.pi*(j-1)/Nw))
varw = 3./8.

# Window the data
nwinf = numpy.floor(Ny/Nw)
nwinh = nwinf - 1
nwin = nwinf + nwinh

# Fill in the windows array
yw = numpy.zeros((Nw,nwin))
yw[:,0:nwin:2] = y[:nwinf*Nw].reshape(Nw,nwinf,order='F').copy()
yw[:,1:(nwin-1):2] = y[(Nw/2):(nwinf-0.5)*Nw].reshape(Nw,nwinh,order='F').copy()

# Taper the data
yt = yw * numpy.tile(w,(nwin,1)).T.shape

# DFT of the data
ythat = numpy.zeros(yt.shape)
ythat = ythat + 0j
for i in range(yt.shape[1]):
	ythat[:,i] = scipy.fft(yt[:,i])
S = (numpy.absolute(ythat)**2)/varw
S = S[0:Nw/2,:]
SdB = 10*numpy.log10(S)
Mw = numpy.arange(0,Nw/2)
fw = Fs * Mw / Nw
tw = numpy.arange(1,nwin) * 0.5 * Nw/Fs


