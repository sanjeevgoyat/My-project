#!/usr/bin/bash
all: lib_simpleloader

lib_simpleloader: loader.c loader.h
	gcc -fPIC -shared -m32 -o lib_simpleloader.so loader.c

clean:
	rm -f lib_simpleloader.so