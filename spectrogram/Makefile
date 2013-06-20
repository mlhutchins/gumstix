DATAFILE = WB20130219003000
FFLAGS = 

.PHONY: test clean

test: $(DATAFILE).png
	open $(DATAFILE).png

$(DATAFILE).png: spectrogram.py 
	python spectrogram.py $(DATAFILE).dat -s

clean:
	rm *png
