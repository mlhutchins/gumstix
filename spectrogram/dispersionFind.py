from spectrogram import *

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
parser.add_argument('-d','--dispersion',action='store_true',help='Plot chirped and de-chirped triggered whistlers.')
parser.add_argument('-f','--force',default = 0.0,type=float, nargs='+',help = 'Forces input times into the list of triggered whistler times')
parser.add_argument('-df','--forceD',default = 0.0,type=float, help = 'Forced dispersion to a given value')
parser.add_argument('-dz','--zoomWindow',default = 0.5,type=float, help = 'Window size (seconds) for calculatin dispersion')

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
dispersionMode = args.dispersion
forcedTrigger = args.force
forcedDispersion = args.forceD
zoomWindow = args.zoomWindow

# Set whistler to be true if either search or dispersion mode is enabled
if whistlerSearch:
	whistler = True
if dispersionMode:
	whistler = True
	whistlerSearch = True

# Set hardcoded parameters
freq = [4., 4.5]

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
		(whistlerTest, triggerTime, freqRange) = whistler_test(SdB,freq)
		
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
		
        # Find trigger time of whistlers in current time window
		trigger = []
		for trig in triggerTime:
			if (trig < tw[time[1]]) and (trig >= tw[time[0]]):
				trigger.append(trig)
		
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
		if zoomMode and len(trigger)>0:
			zoomTime = [find_closest(tw,trigger[0] - zoomWindow),find_closest(tw,trigger[0] + zoomWindow)]
			plt.xlim(zoomTime[0],zoomTime[1])
		else:
			plt.xlim(time[0], time[1])
					
		# Set savename to be filename with updated time increments and the appended text
		name = fileName.split("/")
		name = name[-1]
		saveName = output + name[:-6] + str(i).zfill(2) + appendText + '.png'

        # Set title to give filename and sampling frequency
		plt.title(name + ', Fs: ' + str(Fs[0]/1000) + ' kHz')
			
		# Plot whistler search only if a whistler is detected
		if whistler and whistlerSearch and numpy.sum(whistlerTest[time[0]:time[1]]) > 0:
		
							
			dispersion = numpy.zeros((len(triggerTime),1))
			if dispersionMode:	
				# Get the dispersion of the triggered whistlers
							
				specOrig = {}
				specChirp = {}
				for j in range(len(trigger)):
					
					trig = trigger[j]
					
				# Get the index corresponding to +- zoomWindow around the whistler
					whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
		
					# Cut spectrogram down to lower frequency range
					freqCut = [find_closest(fw,0),find_closest(fw,13*1000)]
		
					# Select just the spectrogram that is near the whistler
					spec = SdB[freqCut[0]:freqCut[1],whistlerLocation[0]:whistlerLocation[1]]
					specOrig[str(j)] = spec
	
					(dispersion[j], chirp) = find_dispersion(spec,fw[freqCut[0]:freqCut[1]].copy())
					specChirp[str(j)] = chirp								
					
			# Plot total energy in the passband as subplot
			fig.add_axes([.1,.05,.8,.15])
			passBand = numpy.sum(SdB[freqRange,:],axis=0)
			plt.plot(tw,passBand)

			ySize = [numpy.min(passBand), numpy.max(passBand)]
			for trig in trigger:
				plt.plot([trig,trig],ySize,'r') 

			plt.xlim(tStart, tEnd)

			plt.title('Spectral Power: %.1f - %.1f kHz, Trigger: %.2f seconds (D = %d)' % (freq[0],freq[1],trigger[0],dispersion[0]))
			
			plt.savefig(saveName,dpi = dpiSetting)
                       
			# Plot zoom of the whistler with de-chirped image in a separate figure
		
			plt.close()

			if dispersionMode:
				
				for j in range(len(trigger)):

					trig = trigger[j]		

					original = specOrig[str(j)]
					dechirp = specChirp[str(j)]

					## Plot normal whistler
					fig = plt.figure(figsize=(imageWidth,imageHeight))
		
					ax1 = fig.add_axes([.1,.1,.4,.8])
					plt.imshow(original, origin='lower',vmin = -40, vmax = -15)
					
					whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
					
					plot_format(ax1, whistlerLocation[0], whistlerLocation[1], int(2.5 / zoomWindow))	
					plt.title(('Trigger: %.2f seconds') % (trig))
	
					## Plot de-chirped whistler
					ax2 = fig.add_axes([.55, .1, .4, .8])
					plt.imshow(dechirp, origin = 'lower', vmin = -40, vmax = -15)

					whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
				
					plot_format(ax2, whistlerLocation[0], whistlerLocation[1], int(2.5 / zoomWindow))						
					plt.title('Dispersion: %d' % (dispersion[j]))

					## Save plot
					# Set savename to be filename with updated time increments and the appended text
					name = fileName.split("/")
					name = name[-1]
					saveName = output + name[:-6] + str(i).zfill(2) + appendText + '_dispersion' + str(j) + '.png'

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
