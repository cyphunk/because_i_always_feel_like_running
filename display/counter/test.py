#!/usr/bin/python2
from __future__ import print_function
import time, threading, traceback, sys

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

class Timer:
    def __init__(self, sec=2.0000, fn=lambda: print(time.time())):
        self.interval = sec
        self.fn = fn
        self._thread = self.go()
    def setinterval(self, sec):
        # diff = sec-self._interval
        # if diff != 0:
        #     self._next_time += sec
        self.interval = sec
    def stop(self):
        self._thread.join()
    @threaded
    def go(self):
        self._next_time = time.time() + self.interval
        while True:
            #                          00:10 - 00:01
            time.sleep( max(0,self._next_time - time.time()) )
            # time.time() == 00:11
            # fn() takes 1 sec
            if self.fn:
                self.fn()
            # time.time() == 00:12
            #                        00:12 - 00:10 is 2
            #self._next_time += (time.time() - self._next_time)
            #   _next_time is now 00:12
            # on next loop sleep will wait 00:12 - 00:12, none
            # effectively the last calc only runtime of fn()
            self._next_time += self.interval - (time.time() - self._next_time)

t=Timer()
while True:
    time.sleep(10)
    t.setinterval(5)
