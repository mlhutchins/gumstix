DATAFILE = WB201302190030
FFLAGS = 

.PHONY: clean test whistler dispersion open

test:
	python spectrogram.py $(DATAFILE)00.dat

whistler:
	python whistlerScan.py $(DATAFILE)00.dat -s

dispersion:
	python dispersionFind.py $(DATAFILE)00.dat
	python dispersionFind.py $(DATAFILE)00.dat -f 13 -d 130

open:
	open $(DATAFILE)*.png

fullTest: test whistler dispersion open

clean:
	rm *png
