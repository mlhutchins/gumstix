import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import argparse

parser = argparse.ArgumentParser(description='Generate spectrograms from wideband WB.dat files')
parser.add_argument('fileName', metavar='filename', type=str, nargs='+', help = 'Name (list) of wideband file(s)')
parser.add_argument('-t','--time', metavar = 'time', default = 15, help = 'Time length of each plot (seconds)')
parser.add_argument('-w','--whistler',action = 'store_true', help = 'Switch to whistler search mode')
parser.add_argument('-o','--output', action='store', metavar='output', default='',type=str,help = 'Output directory')
parser.add_argument('-x','--sizeX', default = 7.5, metavar='width',help = 'Figure width in inches (<4" not recommended)')
parser.add_argument('-y','--sizeY', default = 7.5, metavar='height',help = 'Figure height in inches (<4" not recommended)')
parser.add_argument('-d','--dpi',default = 75, metavar='dpi',help = 'Set image DPI, use for adjusting file size')
parser.add_argument('-a','--append',default = '',type=str,metavar='append',help='Text to append to output filenames')

args = parser.parse_args()
filenames = args.fileName
whistler = args.whistler
timeStep = int(args.time)
output = args.output
imageWidth = float(args.sizeX)
imageHeight = float(args.sizeY)
dpiSetting = float(args.dpi)
appendText = args.append


## Function definitions

def find_closest(A, target):
	#A must be sorted
	idx = A.searchsorted(target)
	idx = numpy.clip(idx, 1, len(A)-1)
	left = A[idx-1]
	right = A[idx]
	idx -= target - left < right - target
	return idx

## Process each listed file
for fileName in filenames:

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
		ythat[:,i] = numpy.fft.fft(yt[:,i])
	S = (numpy.absolute(ythat)**2)/varw
	S = S[0:Nw/2,:]
	SdB = 10*numpy.log10(S)
	Mw = numpy.arange(0,Nw/2)
	fw = Fs * Mw / Nw
	tw = numpy.arange(1,nwin+1) * 0.5 * Nw/Fs

## Test for Whistlers
	if whistler:
		freq = [4., 4.5]
		window = 100
		innerWindow = 10
		threshold = 4
		n = 20
		
		# Select power in frequency range
		freqRange = numpy.arange(find_closest(fw,freq[0]*1000),find_closest(fw,freq[1]*1000))
		band = numpy.sum(SdB[freqRange,:],axis=0)

		# Smooth the data
		weights = numpy.repeat(1.0, n) / n
		band = numpy.convolve(band, weights)[n-1:-(n-1)]

		high = numpy.zeros((len(band),1))
		highSum = high.copy()

		for center in range(window, len(band) - window):
			bandWindow = band[center - window : center + window]
			bandWindow = bandWindow - numpy.min(bandWindow)
			
			prePower = threshold * numpy.mean(bandWindow[:(window - innerWindow)])
			postPower = threshold * numpy.mean(bandWindow[(window + innerWindow):])

			if bandWindow[window] > prePower and bandWindow[window] > postPower:
				high[center] = 1
				highSum[center] = highSum[center - 1] + 1

		step = tw[1] - tw[0]
		whistlerLength = numpy.round(0.05 / step)
		whistlerTest = highSum > whistlerLength
						
## Plotting
	imageSteps = numpy.arange(0,int(numpy.floor(tw[-1])),timeStep)
	
	if whistler:
		freqMax = 13.
		gs = matplotlib.gridspec.GridSpec(3,1,height_ratios=[5,.5,1])
#		gs = matplotlib.gridspec.GridSpec(5,1,height_ratios=[5,.5,1,.5,1])
	else:
		freqMax = (fw[-1]/1000)
	figAspect = 4*timeStep/freqMax
	figAspect = figAspect * (freqMax/24)
	for i in imageSteps:
		fig = plt.figure(figsize=(imageWidth,imageHeight))
		tStart = i
		tEnd = i + timeStep
		time = [find_closest(tw,tStart),find_closest(tw,tEnd)]
		if whistler:
			ax1 = fig.add_subplot(gs[0])
			plt.imshow(SdB, origin='lower',vmin = -40, vmax = -15)
		else:
			ax1 = fig.add_subplot(1,1,1)
			plt.imshow(SdB, origin='lower')
		cbar = plt.colorbar(orientation = 'horizontal')
		cbar.set_label('Spectral Power (dB)')
		plt.xlabel('Time (s)')
		plt.ylabel('Frequency (kHz)')
		tStep = tw[1] - tw[0]
		tStep = int(numpy.round(1 / tStep))
		tickXloc = numpy.arange(0,len(tw),step=tStep)
		tickXlabel = numpy.round(tw[tickXloc])
		fStep = fw[1] - fw[0]
		fStep = fStep/1000
		fStep = int(numpy.round(1 / fStep))
		tickYloc = numpy.arange(0,len(fw),step=2*fStep)
		tickYlabel = numpy.round(fw[tickYloc]/1000)
		plt.xticks(tickXloc,tickXlabel.astype(int))
		plt.yticks(tickYloc,tickYlabel.astype(int))
		plt.xlim(time[0], time[1])
		plt.ylim(0,find_closest(fw,freqMax*1000))
		ax1.set_aspect('auto')
		plt.title(fileName + ', Fs: ' + str(Fs[0]/1000) + ' kHz')
		saveName = output + fileName[:-6] + str(i).zfill(2) + appendText + '.png'
		if whistler and numpy.sum(whistlerTest[time[0]:time[1]]) > 1:
			plt.subplot(gs[2])
	       		plt.plot(tw,numpy.sum(SdB[freqRange,:],axis=0))
	    		plt.xlim(tStart, tEnd)
			plt.title('Spectral Power: ' + str(freq[0]) + ' - ' + str(freq[1]) + ' kHz')
                        plt.savefig(saveName,dpi = dpiSetting)

		elif not whistler:
			plt.savefig(saveName,dpi = dpiSetting)
	
