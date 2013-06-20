OBJECTS = 
FFLAGS = 

.PHONY: test clean

test: WB20130219003000.png
	open WB20130219003000.png

WB20130219003000.png: spectrogram.py 
	python spectrogram.py WB20130219003000.dat -s

clean:
	rm *png
