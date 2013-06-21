import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import argparse

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


	# Add in the forced trigger time
	forced = forcedTrigger
	if forcedTrigger > 0.0 and triggerTime.size > 0:
		triggerTime = numpy.concatenate((triggerTime, forced), axis=0)
		whistlerTest[find_closest(tw,forcedTrigger)] = True
	elif forcedTrigger > 0.0:
		triggerTime = forced
		whistlerTest[find_closest(tw,forcedTrigger)] = True
	
	return (whistlerTest, triggerTime, freqRange)
	
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
	Dtest = numpy.linspace(50,800,21)
	dStep = Dtest[1] - Dtest[0]
	
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
	
	Dtest = numpy.linspace(dispersion-dStep,dispersion+dStep,31)
	 
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
			
	# Force dispersion setting
	
	if not(forcedDispersion == 0.0):
		dispersion = forcedDispersion
	
	# Get de-chirped spectra

	chirp = 0. * spec.copy()
	D = dispersion

	intShift = numpy.ceil(0.5 * D * fShift);

	# Shift each row of spec
	for j in range(len(fRange)):
	
		shiftLevel = -intShift[j]
		chirp[j,:] = numpy.roll(spec[j,:],int(shiftLevel));

	return dispersion, chirp


def plot_format(ax, tStart, tEnd, scale):
	# Set plot labels
	plt.xlabel('Time (s)')
	plt.ylabel('Frequency (kHz)')
	
	# Set X and Y tick marks to be integer values
	tStep = tw[1] - tw[0]
	tStep = int(numpy.round(1 / tStep))/scale
	tickXloc = numpy.arange(tStart,tEnd,step=tStep)
	tickXlabel = numpy.round((scale*2) * tw[tickXloc])/(scale*2)
	fStep = fw[1] - fw[0]
	fStep = fStep/1000
	fStep = int(numpy.round(1 / fStep))
	tickYloc = numpy.arange(0,len(fw),step=2*fStep)
	tickYlabel = numpy.round(fw[tickYloc]/1000)
	plt.xticks(tickXloc - tickXloc[0],tickXlabel)
	plt.yticks(tickYloc,tickYlabel.astype(int))
		
	plt.ylim(0,find_closest(fw,freqMax*1000))
	
	# Aspect ratio to fill entire plot
	ax.set_aspect('auto')

def import_wideband(filename):

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

	return (t, y, Fs)
	
def spectrogram_fft(y, Fs):

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
	
	return (tw, fw, SdB)
	
if __name__ == "__main__":

	# Setup the structure for the input options and arguments
	parser = argparse.ArgumentParser(description='Generate spectrograms from wideband WB.dat files')
	parser.add_argument('fileName', metavar='filename', type=str, nargs='+', help = 'Name (list) of wideband file(s)')
	parser.add_argument('-t','--time', metavar = 'time', default = 15, help = 'Time length of each plot (seconds)')
	parser.add_argument('-w','--whistler',action = 'store_true', help = 'Switch to whistler search plots')
	parser.add_argument('-o','--output', action='store', metavar='output', default='',type=str,help = 'Output directory')
	parser.add_argument('-x','--sizeX', default = 7.5, metavar='width',help = 'Figure width in inches (<4" not recommended)')
	parser.add_argument('-y','--sizeY', default = 7.5, metavar='height',help = 'Figure height in inches (<4" not recommended)')
	parser.add_argument('-r','--dpi',default = 75, metavar='dpi',help = 'Set image DPI, use for adjusting file size')
	parser.add_argument('-a','--append',default = '',type=str,metavar='append',help='Text to append to output filenames')
	parser.add_argument('-v','--verbose',action='store_true',help = 'Verbose mode - list files being processed')

	args = parser.parse_args()
	filenames = args.fileName
	whistler = args.whistler
	timeStep = int(args.time)
	output = args.output
	imageWidth = float(args.sizeX)
	imageHeight = float(args.sizeY)
	dpiSetting = float(args.dpi)
	appendText = args.append
	verboseMode = args.verbose

	## Process each listed file
	for fileName in filenames:

		## Print out filename if in verbose mode
		if verboseMode:
			print fileName

		## Import Wideband
	
		(t, y, Fs) = import_wideband(fileName)
	
		## Spectrogram ##

		(tw, fw, SdB) = spectrogram_fft(y, Fs)	

# 		## Get whistler data
# 		if whistler:
# 			(whistlerTest, triggerTime, freqRange) = whistler_test(SdB,freq)
# 		
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
		
			# Plot the spectrogram and set colorbar limits for whistler case
			if whistler:
				ax1 = fig.add_axes([.1,.3,.8,.6])
				plt.imshow(SdB, origin='lower',vmin = -40, vmax = -15)
			else:
				ax1 = fig.add_subplot(1,1,1)
				plt.imshow(SdB, origin='lower')
			
				# Generate and label colorbar
				cbar = plt.colorbar(orientation = 'horizontal')
				cbar.set_label('Spectral Power (dB)')
		
			# Format plot
			plot_format(ax1,0, len(tw), 1)
		
			# Set the spectrogram view limits
			plt.xlim(time[0], time[1])
					
			# Set savename to be filename with updated time increments and the appended text
			name = fileName.split("/")
			name = name[-1]
			saveName = output + name[:-6] + str(i).zfill(2) + appendText + '.png'

			# Set title to give filename and sampling frequency
			plt.title(name + ', Fs: ' + str(Fs[0]/1000) + ' kHz')
			
			# Plot whistler high contrast plot
			if whistler:
				# Plot total energy in the passband as subplot
				fig.add_axes([.1,.05,.8,.15])
				plt.plot(tw,numpy.sum(SdB[freqRange,:],axis=0))
				plt.xlim(tStart, tEnd)
				plt.title('Spectral Power: %.1f - %.1f kHz' % (freq[0],freq[1]))
				plt.savefig(saveName,dpi = dpiSetting)
						
			# Plot normal spectrogram
			else:
				plt.savefig(saveName,dpi = dpiSetting)
		
			# Close the plot
			plt.close()	
