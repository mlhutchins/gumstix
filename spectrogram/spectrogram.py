import scipy
import numpy
import matplotlib
import sys
import argparse
from pylab import *

parser = argparse.ArgumentParser(description='Generate spectrograms from wideband WB.dat files')
parser.add_argument('fileName',metavar='filename',type=str,help = 'Name of wideband file')
parser.add_argument('--time', default = 15, help = 'Time length of each plot (seconds)')
parser.add_argument('--whistler',action = 'store_true', help = 'Switch to whistler search mode')

args = parser.parse_args()
print args
fileName = args.fileName
whistler = args.whistler
timeStep = int(args.time)

## Read in Wideband VLF Data

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
yt = yw * numpy.tile(w,(nwin,1)).T

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
tw = numpy.arange(1,nwin+1) * 0.5 * Nw/Fs

## Plotting

def find_closest(A, target):
    #A must be sorted
    idx = A.searchsorted(target)
    idx = numpy.clip(idx, 1, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left < right - target
    return idx

imageSteps = numpy.arange(0,int(floor(tw[-1])),timeStep)

if whistler:
	freqMax = 13.
	gs = matplotlib.gridspec.GridSpec(5,1,height_ratios=[5,.5,1,.5,1])
else:
	freqMax = (fw[-1]/1000)
figAspect = 4*timeStep/freqMax
figAspect = figAspect * (freqMax/24)
for i in imageSteps:
	fig = figure(figsize=(7.5,7.5))
	tStart = i
	tEnd = i + timeStep
	time = [find_closest(tw,tStart),find_closest(tw,tEnd)]
	if whistler:
		ax1 = fig.add_subplot(gs[0])
		imshow(SdB, origin='lower',vmin = -40, vmax = -15)
	else:
                ax1 = fig.add_subplot(1,1,1)
		imshow(SdB, origin='lower')
	cbar = colorbar(orientation = 'horizontal')
	cbar.set_label('Spectral Power (dB)')
	xlabel('Time (s)')
	ylabel('Frequency (kHz)')
	tStep = tw[1] - tw[0]
	tStep = int(numpy.round(1 / tStep))
	tickXloc = numpy.arange(0,len(tw),step=tStep)
	tickXlabel = numpy.round(tw[tickXloc])
	fStep = fw[1] - fw[0]
	fStep = fStep/1000
	fStep = int(numpy.round(1 / fStep))
	tickYloc = numpy.arange(0,len(fw),step=2*fStep)
	tickYlabel = numpy.round(fw[tickYloc]/1000)
	xticks(tickXloc,tickXlabel)
	yticks(tickYloc,tickYlabel)
	xlim(time[0], time[1])
	ylim(0,find_closest(fw,freqMax*1000))
	ax1.set_aspect('auto')
	title(fileName + ', Fs: ' + str(int(Fs[0]/1000)) + ' kHz')
	saveName = fileName[:-6] + str(i) + '.png'
	if whistler:
		subplot(gs[2])
		freq = [3.5, 7.]
		freqRange = numpy.arange(find_closest(fw,freq[0]*1000),find_closest(fw,freq[1]*1000))
		plot(tw,numpy.sum(SdB[freqRange,:],axis=0))
		xlim(tStart, tEnd)
                title('Spectral Power: ' + str(freq[0]) + ' - ' + str(freq[1]) + ' kHz')

                subplot(gs[4])
                freq = [4., 5.]
                freqRange = numpy.arange(find_closest(fw,freq[0]*1000),find_closest(fw,freq[1]*1000))
                plot(tw,numpy.sum(SdB[freqRange,:],axis=0))
                xlim(tStart, tEnd)
		title('Spectral Power: ' + str(freq[0]) + ' - ' + str(freq[1]) + ' kHz')
	
	savefig(saveName)

