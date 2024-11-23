#!usr/bin/bash
all:
	$(MAKE) -C loader
	$(MAKE) -C launcher
	$(MAKE) -C test

	cp loader/lib_simpleloader.so bin/
	cp launcher/launch bin/
	./launcher/launch test/sum
	./launcher/launch test/fib

clean:
	$(MAKE) -C loader
	$(MAKE) -C launcher
	$(MAKE) -C test
