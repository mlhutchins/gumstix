from spectrogram import *

# Setup the structure for the input options and arguments
parser = argparse.ArgumentParser(description='Generate dispersion plots for triggered or manual whistler locations in VLF wideband WB.dat files')
parser.add_argument('fileName', metavar='filename', type=str, nargs='+', help = 'Name (list) of wideband file(s)')
parser.add_argument('-t','--time', metavar = 'time', default = 15, help = 'Time length of each plot (seconds)')
parser.add_argument('-o','--output', action='store', metavar='output', default='',type=str,help = 'Output directory')
parser.add_argument('-x','--sizeX', default = 7.5, metavar='width',help = 'Figure width in inches (<4" not recommended)')
parser.add_argument('-y','--sizeY', default = 7.5, metavar='height',help = 'Figure height in inches (<4" not recommended)')
parser.add_argument('-r','--dpi',default = 75, metavar='dpi',help = 'Set image DPI, use for adjusting file size')
parser.add_argument('-a','--append',default = '',type=str,metavar='append',help='Text to append to output filenames')
parser.add_argument('-v','--verbose',action='store_true',help = 'Verbose mode - list files being processed')
parser.add_argument('-f','--forceT',default = 0.0,type=float, nargs='+',help = 'Forces input times into the list of triggered whistler times')
parser.add_argument('-d','--forceD',default = 0.0,type=float, help = 'Forced dispersion to a given value')
parser.add_argument('-z','--zoomWindow',default = 0.5,type=float, help = 'Window size (seconds) for calculatin dispersion')

args = parser.parse_args()
filenames = args.fileName
timeStep = int(args.time)
output = args.output
imageWidth = float(args.sizeX)
imageHeight = float(args.sizeY)
dpiSetting = float(args.dpi)
appendText = args.append
verboseMode = args.verbose
forcedTrigger = args.forceT
forcedDispersion = args.forceD
zoomWindow = args.zoomWindow

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
	(whistlerTest, triggerTime, freqRange) = whistler_test(SdB, freq, tw, fw)
		
	# Add in the forced trigger time
	forced = forcedTrigger
	if forcedTrigger > 0.0 and triggerTime.size > 0:
		triggerTime = numpy.concatenate((triggerTime, forced), axis=0)
		whistlerTest[find_closest(tw,forcedTrigger)] = True
	elif forcedTrigger > 0.0:
		triggerTime = forced
		whistlerTest[find_closest(tw,forcedTrigger)] = True
			
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
		
		# Plot whistler search only if a whistler is detected
		if numpy.sum(whistlerTest[time[0]:time[1]]) > 0:
			
			for j in range(len(trigger)):
				
				trig = trigger[j]
				
				# Get the index corresponding to +- zoomWindow around the whistler
				whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
	
				# Cut spectrogram down to lower frequency range
				freqCut = [find_closest(fw,0),find_closest(fw,13*1000)]
	
				# Select just the spectrogram that is near the whistler
				spec = SdB[freqCut[0]:freqCut[1],whistlerLocation[0]:whistlerLocation[1]]

				fRange = fw[freqCut[0]:freqCut[1]]
				(dispersion, dechirp) = find_dispersion(spec,fRange, tw)

				# Force dispersion setting
				if not(forcedDispersion == 0.0):
					D = forcedDispersion
					
					# Get de-chirped spectra
					dechirp = dechirp(spec, D, tw, fRange)
	
				## Plot normal whistler
				fig = plt.figure(figsize=(imageWidth,imageHeight))
	
				ax1 = fig.add_axes([.1,.1,.4,.8])
				plt.imshow(spec, origin='lower',vmin = -40, vmax = -15)
								
				plot_format(ax1, whistlerLocation[0], whistlerLocation[1], int(2.5 / zoomWindow), tw, fw, freqMax)	
				plt.title(('Trigger: %.2f seconds') % (trig))

				## Plot de-chirped whistler
				ax2 = fig.add_axes([.55, .1, .4, .8])
				plt.imshow(dechirp, origin = 'lower', vmin = -40, vmax = -15)

				whistlerLocation = [find_closest(tw,trig - zoomWindow),find_closest(tw,trig + zoomWindow)]
			
				plot_format(ax2, whistlerLocation[0], whistlerLocation[1], int(2.5 / zoomWindow), tw, fw, freqMax)						
				plt.title('Dispersion: %d' % (dispersion))

				## Save plot
				# Set savename to be filename with updated time increments and the appended text
				name = fileName.split("/")
				name = name[-1]
				saveName = output + name[:-6] + str(i).zfill(2) + appendText + '_dispersion' + str(j) + '.png'

				plt.savefig(saveName,dpi = dpiSetting)

		
		# Close the plot
		plt.close()	
