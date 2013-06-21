DATAFILE = WB201302190030
FFLAGS = 

.PHONY: clean test whistler dispersion

test:
	python spectrogram.py $(DATAFILE)00.dat
	open $(DATAFILE)*.png

whistler:
	python whistlerScan.py $(DATAFILE)00.dat -s
	open $(DATAFILE)*.png

dispersion:
	python dispersionFind.py $(DATAFILE)00.dat
	open $(DATAFILE)*.png
	python dispersionFind.py $(DATAFILE)00.dat -f 13 -d 130
	open $(DATAFILE)*.png

fullTest: test whistler dispersion

clean:
	rm *png
