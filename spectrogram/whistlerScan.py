from spectrogram import *

# Setup the structure for the input options and arguments
parser = argparse.ArgumentParser(description='Searches for whistlers in wideband WB.dat files')
parser.add_argument('fileName', metavar='filename', type=str, nargs='+', help = 'Name (list) of wideband file(s)')
parser.add_argument('-t','--time', metavar = 'time', default = 15, help = 'Time length of each plot (seconds)')
parser.add_argument('-o','--output', action='store', metavar='output', default='',type=str,help = 'Output directory')
parser.add_argument('-x','--sizeX', default = 7.5, metavar='width',help = 'Figure width in inches (<4" not recommended)')
parser.add_argument('-y','--sizeY', default = 7.5, metavar='height',help = 'Figure height in inches (<4" not recommended)')
parser.add_argument('-r','--dpi',default = 75, metavar='dpi',help = 'Set image DPI, use for adjusting file size')
parser.add_argument('-a','--append',default = '',type=str,metavar='append',help='Text to append to output filenames')
parser.add_argument('-s','--search',action= 'store_true',help = 'Only output images when a whistler is detected')
parser.add_argument('-v','--verbose',action='store_true',help = 'Verbose mode - list files being processed')
parser.add_argument('-d','--dispersion',action='store_true',help='Calculated dispersion for triggered whistlers.')

args = parser.parse_args()
filenames = args.fileName
timeStep = int(args.time)
output = args.output
appendText = args.append
whistlerSearch = args.search
verboseMode = args.verbose
dispersionMode = args.dispersion
imageWidth = float(args.sizeX)
imageHeight = float(args.sizeY)
dpiSetting = float(args.dpi)

# Set hardcoded parameters
freq = [4., 4.5]

## Process each listed file
for fileName in filenames:

## Print out filename if in verbose mode
	if verboseMode:
		print fileName
		
	## Import Wideband

	(t, y, Fs) = import_wideband(fileName)

	## Spectrogram ##

	(tw, fw, SdB) = spectrogram_fft(y, Fs)	

	## Get whistler data

	(whistlerTest, triggerTime, freqRange) = whistler_test(SdB,freq,tw,fw)
				
	## Plotting
	# Number of images
	imageSteps = numpy.arange(0,int(numpy.floor(tw[-1])),timeStep)
	
	freqMax = 13.

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
		ax1 = fig.add_axes([.1,.3,.8,.6])
		plt.imshow(SdB, origin='lower',vmin = -40, vmax = -15)
	
		# Format plot
		plot_format(ax1,0, len(tw), 1, tw, fw, freqMax)
		
		# Set the spectrogram view limits
		plt.xlim(time[0], time[1])
					
		# Set savename to be filename with updated time increments and the appended text
		name = fileName.split("/")
		name = name[-1]
		saveName = output + name[:-6] + str(i).zfill(2) + appendText + '.png'

        # Set title to give filename and sampling frequency
		plt.title(name + ', Fs: ' + str(Fs[0]/1000) + ' kHz')
			
		# Plot whistler search only if a whistler is detected
		if whistlerSearch and numpy.sum(whistlerTest[time[0]:time[1]]) > 0:
		
			dispersion = numpy.zeros((len(triggerTime),1))
			if dispersionMode:	
				# Get the dispersion of the triggered whistlers
				for j in range(len(trigger)):
					
					trig = trigger[j]
					
					# Get the index corresponding to +- zoomWindow around the whistler
					whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
		
					# Cut spectrogram down to lower frequency range
					freqCut = [find_closest(fw,0),find_closest(fw,13*1000)]
		
					# Select just the spectrogram that is near the whistler
					spec = SdB[freqCut[0]:freqCut[1],whistlerLocation[0]:whistlerLocation[1]]
	
					(dispersion[j], chirp) = find_dispersion(spec,fw[freqCut[0]:freqCut[1]].copy())
					
			# Plot total energy in the passband as subplot
			fig.add_axes([.1,.05,.8,.15])
			passBand = numpy.sum(SdB[freqRange,:],axis=0)
			plt.plot(tw,passBand)

			ySize = [numpy.min(passBand), numpy.max(passBand)]
			for trig in trigger:
				plt.plot([trig,trig],ySize,'r') 

			plt.xlim(tStart, tEnd)

			if dispersionMode:
				plt.title('Spectral Power: %.1f - %.1f kHz, Trigger: %.2f seconds (D = %d)' % (freq[0],freq[1],trigger[0],dispersion[0]))
			else:
				plt.title('Spectral Power: %.1f - %.1f kHz, Trigger: %.2f seconds' % (freq[0],freq[1],trigger[0]))
				
			plt.savefig(saveName,dpi = dpiSetting)

		# Plot whistler high contrast plot
		elif not whistlerSearch:
			# Plot total energy in the passband as subplot
			fig.add_axes([.1,.05,.8,.15])
			plt.plot(tw,numpy.sum(SdB[freqRange,:],axis=0))
			plt.xlim(tStart, tEnd)
			plt.title('Spectral Power: %.1f - %.1f kHz' % (freq[0],freq[1]))
			plt.savefig(saveName,dpi = dpiSetting)
                        
		# Close the plot
		plt.close()	
