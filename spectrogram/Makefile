DATAFILE = WB201302190030
FFLAGS = 

.PHONY: clean

test:
	python spectrogram.py $(DATAFILE)00.dat
	open $(DATAFILE)*.png
whistler:
	python whistlerScan.py $(DATAFILE)00.dat -s
	open $(DATAFILE)*.png

clean:
	rm *png
