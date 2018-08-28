RGB_INCDIR=../libs/rpi-rgb-led-matrix/include
RGB_LIBDIR=../libs/rpi-rgb-led-matrix/lib

CFLAGS=-I$(RGB_INCDIR) -Wall -O3 -g -Wextra -Wno-unused-parameter
LFLAGS=-L$(RGB_LIBDIR) -lrgbmatrix -lrt -lm -lpthread -lconfig++ -llo

all: clock counter brightness osc-send

clock.o: clock.cc
	g++ $(CFLAGS) -c -o $@ $<
clock: clock.o
	g++ $< -o $@ $(LFLAGS)

counter.o: counter.cc
	g++ $(CFLAGS) -c -o $@ $<
counter: counter.o
	g++ $< -o $@ $(LFLAGS)

brightness.o: brightness.cc
	g++ $(CFLAGS) -c -o $@ $<
brightness: brightness.o
	g++ $< -o $@ $(LFLAGS)

osc-send.o: osc-send.c
	g++ $(CFLAGS) -c -o $@ $<
osc-send: osc-send.o
	g++ $< -o $@ -llo

clean:
	rm -f *.o clock counter brightness osc-send
