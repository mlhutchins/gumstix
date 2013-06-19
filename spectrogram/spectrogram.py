import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import argparse

# Setup the structure for the input options and arguments
parser = argparse.ArgumentParser(description='Generate spectrograms from wideband WB.dat files')
parser.add_argument('fileName', metavar='filename', type=str, nargs='+', help = 'Name (list) of wideband file(s)')
parser.add_argument('-t','--time', metavar = 'time', default = 15, help = 'Time length of each plot (seconds)')
parser.add_argument('-w','--whistler',action = 'store_true', help = 'Switch to whistler search mode')
parser.add_argument('-o','--output', action='store', metavar='output', default='',type=str,help = 'Output directory')
parser.add_argument('-x','--sizeX', default = 7.5, metavar='width',help = 'Figure width in inches (<4" not recommended)')
parser.add_argument('-y','--sizeY', default = 7.5, metavar='height',help = 'Figure height in inches (<4" not recommended)')
parser.add_argument('-r','--dpi',default = 75, metavar='dpi',help = 'Set image DPI, use for adjusting file size')
parser.add_argument('-a','--append',default = '',type=str,metavar='append',help='Text to append to output filenames')
parser.add_argument('-s','--search',action= 'store_true',help = 'Only output images when a whistler is detected')
parser.add_argument('-v','--verbose',action='store_true',help = 'Verbose mode - list files being processed')
parser.add_argument('-z','--zoom',action='store_true',help = 'Save only the spectrogram within +-0.5 seconds of trigger')
parser.add_argument('-d','--dispersion',default = -1, metavar='dispersion',help='Calculated dispersion for specified event (given in seconds from start of file')

args = parser.parse_args()
filenames = args.fileName
whistler = args.whistler
timeStep = int(args.time)
output = args.output
imageWidth = float(args.sizeX)
imageHeight = float(args.sizeY)
dpiSetting = float(args.dpi)
appendText = args.append
whistlerSearch = args.search
verboseMode = args.verbose
zoomMode = args.zoom
dispersionStart = args.dispersion

# If dispersionStart is not set than disable dispersion mode
if dispersionStart == -1:
	dispersionMode = False
else:
	dispersionMode = True

# Set whistler to be true if either search or dispersion mode is enabled
if whistlerSearch or dispersionMode:
	whistler = True

# Set hardcoded parameters
freq = [4., 4.5]
zoomWindow = 0.5

## Function definitions

# Find closest gets the index in A that is closest to target
def find_closest(A, target):
	#A must be sorted
	idx = A.searchsorted(target)
	idx = numpy.clip(idx, 1, len(A)-1)
	left = A[idx-1]
	right = A[idx]
	idx -= target - left < right - target
	return idx



## Test for Whistlers
def whistler_test(SdB, freq):

	# Define the time step
	tStep = tw[1] - tw[0]

	# Initialize arrays
	highSum = numpy.zeros((len(tw),1))


	# Set the minimum length of a whistler
	whistlerLength = 0.05 / tStep

	# How large of a window to use for the pre and post whistler energy
	window = int(numpy.round(1/tStep))

	# Estimated length of a whistler, +-innerWindow not used in the mean pre/post energy
	innerWindow = int(numpy.round(0.1/tStep))

	# Threshold is how much larger a whistler needs to be than the nearby noise
	threshold = 4.

	# Size of the smoothing filter
	n = 20
	
	# Select power in frequency range
	freqRange = numpy.arange(find_closest(fw,freq[0]*1000),find_closest(fw,freq[1]*1000))
	band = numpy.sum(SdB[freqRange,:],axis=0)

	# Smooth the data
	weights = numpy.repeat(1.0, n) / n
	band = numpy.convolve(band, weights)[n-1:-(n-1)]

	# Run through the band except for the first and last window points
	for center in range(window, len(highSum) - window):
		bandWindow = band[center - window : center + window]
		
		# Normalize the data to the lowest point in the bandWindow
		bandWindow = bandWindow - numpy.min(bandWindow)
		
		# Get the pre and post test point energy
		prePower = threshold * numpy.mean(bandWindow[:(window - innerWindow)])
		postPower = threshold * numpy.mean(bandWindow[(window + innerWindow):])

		# Compare the current point to the nearby noise level
		if bandWindow[window] > prePower and bandWindow[window] > postPower:
						highSum[center] = highSum[center - 1] + 1

	# Check for any sustained signal longer then a whistler length
	whistlerTest = highSum > whistlerLength

	# Remove successive triggers (leading edge trigger)
	for i in range(len(whistlerTest)-1):
		n = len(whistlerTest)
		if whistlerTest[n-i-1]:
			whistlerTest[n-i] = False

	# Record the trigger times
	triggerTime = tw[whistlerTest[:,0]]

	return [whistlerTest, triggerTime, freqRange]

## Function to find the best fitting dispersion for the input spectrogram
def find_dispersion(SdB, fRange):

	## Crude dispersion calculation
	
	# Get the left shift-vector in seconds for a D = 1 constant
	
	fRange[0] = fRange[1]
	fShift = 1./numpy.sqrt(fRange)
	
	# Convert to seconds in units of time step
	fSamp = 1./(tw[1]-tw[0])
	fShift = fSamp * fShift
	
	# Generate a coarse index to shift each frequency to de-chirp it
	Dtest = numpy.linspace(100,200,11)
	
	# Initialize output array
	power = numpy.zeros((len(Dtest),spec.shape[0]))
	
	for i in range(len(Dtest)):
	
		shift = 0. * spec.copy()
		
		D = Dtest[i]
		
		intShift = numpy.ceil(0.5 * D * fShift);

		# Shift each row of spec
		for j in range(len(fRange)):
			
			shiftLevel = -intShift[j]
			shift[j,:] = numpy.roll(spec[j,:],int(shiftLevel));
			
			# Get total power in each column
			
			power[i,:] = numpy.sum(shift,1)**4
		
	power = numpy.sum(power,axis=1)
	dispersion = Dtest[power == numpy.max(power)]
		
	if len(dispersion) > 1:
		if verboseMode:
			print 'Multiple Dispersions: ' + str(dispersion)
			print 'Choosing: ' + str(dispersion[0])
		dispersion = dispersion[0]
			
	## Fine dispersion calculation
	
	Dtest = numpy.linspace(dispersion-10,dispersion+10,21)
	 
	# Initialize output array
	power = numpy.zeros((len(Dtest),spec.shape[0]))
		
	for i in range(len(Dtest)):
			
		shift = 0. * spec.copy()
		
		D = Dtest[i]
		
		intShift = numpy.ceil(0.5 * D * fShift);

		# Shift each row of spec
		for j in range(len(fRange)):
			
			shiftLevel = -intShift[j]
			shift[j,:] = numpy.roll(spec[j,:],int(shiftLevel));
			
			# Get total power in each column
			
			power[i,:] = numpy.sum(shift,1)**4
			

	power = numpy.sum(power,axis=1)

	dispersion = Dtest[power == numpy.max(power)]
	if len(dispersion) > 1:
		if verboseMode:
			print 'Multiple Dispersions: ' + str(dispersion)
			print 'Choosing: ' + str(dispersion[0])
		dispersion = dispersion[0]
			
	#else:
	#	if verboseMode:
	#		print 'No Single Dispersion Found: ' + str(dispersion)
	#	dispersion = 0

	return dispersion

## Process each listed file
for fileName in filenames:

## Print out filename if in verbose mode
	if verboseMode:
		print fileName

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

	# Get whistler data
	if whistler:
		test = whistler_test(SdB,freq)
		whistlerTest = test[0]
		triggerTime = test[1]
		freqRange = test[2]

	## Plotting
	# Number of images
	imageSteps = numpy.arange(0,int(numpy.floor(tw[-1])),timeStep)
	
	if whistler:
		# Maximum frequency to plot in whistler search
		freqMax = 13.
	else:
		# Maximum frequency to plot spectrogram based on the FFT harmonics
		freqMax = (fw[-1]/1000)
	
	# Plot each image
	for i in imageSteps:
		# Initialize figure
		fig = plt.figure(figsize=(imageWidth,imageHeight))
		
		# Get start and end of the time window
		tStart = i
		tEnd = i + timeStep
		time = [find_closest(tw,tStart),find_closest(tw,tEnd)]
		

        # Find trigger time of whistlers
		if whistler and numpy.sum(whistlerTest[time[0]:time[1]]) > 0:
			trigger = triggerTime[numpy.logical_and(tw[time[0]] <= triggerTime, triggerTime <= tw[time[1]])]
		else:
			trigger = []


		# Plot the spectrogram and set colorbar limits for whistler case
		if whistler:
			#ax1 = fig.add_subplot(2,1,1)
			ax1 = fig.add_axes([.1,.3,.8,.6])
			plt.imshow(SdB, origin='lower',vmin = -40, vmax = -15)
		else:
			ax1 = fig.add_subplot(1,1,1)
			plt.imshow(SdB, origin='lower')
			
			# Generate and label colorbar
			cbar = plt.colorbar(orientation = 'horizontal')
			cbar.set_label('Spectral Power (dB)')
		
		# Set plot labels
		plt.xlabel('Time (s)')
		plt.ylabel('Frequency (kHz)')
		
		# Set X and Y tick marks to be integer values
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
		
		# Set the spectrogram view limits
		if zoomMode and len(trigger)>0:
			zoomTime = [find_closest(tw,trigger[0] - zoomWindow),find_closest(tw,trigger[0] + zoomWindow)]
			plt.xlim(zoomTime[0],zoomTime[1])
		else:
			plt.xlim(time[0], time[1])
		plt.ylim(0,find_closest(fw,freqMax*1000))
		
		# Aspect ratio to fill entire plot
		ax1.set_aspect('auto')
		
		# Set savename to be filename with updated time increments and the appended text
		name = fileName.split("/")
		name = name[-1]
		saveName = output + name[:-6] + str(i).zfill(2) + appendText + '.png'

        # Set title to give filename and sampling frequency
		plt.title(name + ', Fs: ' + str(Fs[0]/1000) + ' kHz')
			
		# Plot whistler search only if a whistler is detected
		if whistler and whistlerSearch and numpy.sum(whistlerTest[time[0]:time[1]]) > 0:
			
			# Get the dispersion of the triggered whistlers
						
			dispersion = numpy.zeros((len(triggerTime),1))
		
			for i in range(len(triggerTime)):
				
				trig = triggerTime[i]
				
			# Get the index corresponding to +- zoomWindow around the whistler
				whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
	
				# Cut spectrogram down to lower frequency range
				freqCut = [find_closest(fw,0),find_closest(fw,13*1000)]
	
				# Select just the spectrogram that is near the whistler
				spec = SdB[freqCut[0]:freqCut[1],whistlerLocation[0]:whistlerLocation[1]]
				
				dispersion[i] = find_dispersion(spec,fw[freqCut[0]:freqCut[1]].copy())
								
					
			# Plot total energy in the passband as subplot
			fig.add_axes([.1,.05,.8,.15])
			passBand = numpy.sum(SdB[freqRange,:],axis=0)
			plt.plot(tw,passBand)

			ySize = [numpy.min(passBand), numpy.max(passBand)]
			for triggerTime in trigger:
				plt.plot([triggerTime,triggerTime],ySize,'r') 

			plt.xlim(tStart, tEnd)

			plt.title('Spectral Power: %.1f - %.1f kHz, Trigger: %.2f seconds (D = %d)' % (freq[0],freq[1],trigger[0],dispersion[0]))
			
			plt.savefig(saveName,dpi = dpiSetting)
                        
		# Plot whistler high contrast plot
		elif whistler and not whistlerSearch:
			# Plot total energy in the passband as subplot
			fig.add_axes([.1,.05,.8,.15])
			plt.plot(tw,numpy.sum(SdB[freqRange,:],axis=0))
			plt.xlim(tStart, tEnd)
			plt.title('Spectral Power: %.1f - %.1f kHz' % (freq[0],freq[1]))
			plt.savefig(saveName,dpi = dpiSetting)
                        
		# Plot normal spectrogram
		elif not whistler:
			plt.savefig(saveName,dpi = dpiSetting)
		
		# Close the plot
		plt.close()	
