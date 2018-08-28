#!/usr/bin/python
# incoming osc integers 0<>100 are processed and sent to counter osc
from __future__ import print_function
import liblo
import sys, os, time, threading, traceback

counter_osc_host = 'localhost'
counter_osc_port = 9000
server_osc_port  = 9001

DEBUG=True
USE_AMPLITUDE=True # modify range of output based on current hr

try:
    counter = liblo.Address(counter_osc_host, counter_osc_port)
    server  = liblo.ServerThread(server_osc_port)
except liblo.ServerError as err:
    print(err)
    sys.exit()


# Generic timer thread
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
        self.paused = False
        self._thread = self.go()
    def setinterval(self, sec):
        self.interval = sec
    def pause(self):
        self.paused = True
    def unpause(self):
        self.paused = False
    @threaded
    def go(self):
        while True:
            if self.paused == True:
                time.sleep(0.01) # move the timer forward
                continue
            time.sleep( max(0,self.interval) )
            if self.fn:
                self.fn()

    @threaded
    def go_old(self):
        # this method ideally doesnt drift or add time due to processing time
        # but, when the system is under a load there is some error where it
        # looses its interval and gets very close to 0
        self._next_time = time.time() + self.interval
        while True:
            if self.paused == True:
                time.sleep(0.01) # move the timer forward
                self._next_time += (time.time() - self._next_time)
                continue
            time.sleep( max(0,self._next_time - time.time()) )
            if self.fn:
                self.fn()
            self._next_time += self.interval - (time.time() - self._next_time)


def convert_range(in_val, in_min, in_max, out_min, out_max):
    # take current hr value and convert it to change
    # python2 ignores float if one val not float:
    percent = (float(in_val) - in_min) / (in_max - in_min)
    # (x - 0) / (100 - 0)
    val = ((out_max - out_min) * percent) + out_min
    # ((100 - 1) * %) + 1
    return val

# Heart Rate
# convert incoming hr values (set()) into outgoing osc
if DEBUG:
    tmpcount=0
    tmpcounttime=time.time()
class HR:
    def __init__(hr, min=60.0, max=220.0):
        # Values user we may change:
        hr.min = float(min) # hr value under this ignored
        hr.max = float(max) # hr value over this ignored
        hr.out_min = 0.0        # osc out min (hr transposed to this)
        hr.out_max = 100.0      # osc out max (hr transposed to this)
        # the delay for changer that smooths hr value changes:
        hr.changer_rate = 0.3 # 0.6=60 seconds to trans from 80->180
        # Start paused?
        hr.paused = True # True will cause it to animate out

        # current hr:
        hr.current = float(min)
        # set when changing new new hr with set()
        # see hr_curv, hr_ease, set
        hr.target = float(min)
        # transition timer used to smooth on hrset
        # 0.6 = would take 60 seconds to go from 80bpm to 180
        hr.changer = Timer(hr.changer_rate, hr.change_curve)


        # used by _linearSaw:
        hr.output_current = 0.0 # this will change between 0<>100
        hr._tmp = 0.0
        # TODO: atm we cannot set an arbitrary max, e.g. 50
        #       that means that counter will have to process values
        #       at 0<>100 could treat these as percentages
        # Internal can ignore

        # Animation/Output timer
        # we assume send no more than 100 events/osc messages per beat.
        # Eg. hr=60 is 1 beat sec, 100 events, Timer interval of 0.01
        hr.outputer = Timer(60.0/100.0/hr.current, hr.output_linear_saw)


    def change_curve(hr):
        if hr.current == hr.target:
            hr.changer.pause()
            return
        if hr.current < hr.target:
            hr.current += 1
        else:
            hr.current -= 1
        hr.outputer.setinterval( 60.0/100.0/hr.current )
    def pause(hr):
        hr.paused = True     # stop sending osc
        # outputer function instead pauses self when max int reached
        #hr.outputer.pause()  # stop data output
    def unpause(hr):
        hr.paused = False      # stop sending osc
        hr.outputer.unpause()  # stop data output
        hr.changer.unpause()
    def set(hr, newhr):
        if hr.target != newhr:
            if newhr > hr.max:
                newhr = hr.max
            elif newhr < hr.min:
                newhr = hr.min
            hr.target = newhr
            hr.unpause()

    def output_linear_saw(hr):
        # this will be called 100 times
        hr.output_current += 1
        # hr.output_current += min(1, ( hr.out_max-hr.out_min )/100)
        if DEBUG:
            global tmpcount
            tmpcount += 1
        if hr.output_current > 100:
        # if hr.output_current > ( hr.out_max-hr.out_min ):
            hr.output_current = 0
            if DEBUG:
                t = time.time()
                global tmpcounttime
                print("one saw = %d bangs in %f seconds (%f)"%(tmpcount, t-tmpcounttime, hr.current))
                tmpcount=0
                tmpcounttime=t


        # TODO: resolve python2 issues
        # # increase amplitude of output based on how high HR in range
        if USE_AMPLITUDE:
            percent = (hr.current - hr.min) / (hr.max - hr.min)
            # print("pe %d*%0.4f = %d "%(100,percent,100*percent))
            out_min = max(0.0, (hr.out_max*0.7)-(100.0 * percent)) # play with 90
            oscvalue = convert_range(hr.output_current,0,100,out_min,hr.out_max)
        else:
            oscvalue = convert_range(hr.output_current,0,100,hr.out_min,hr.out_max)

        # send OSC message
        if int(oscvalue) != int(hr._tmp):
            liblo.send(counter, 'int', int(oscvalue))
            hr._tmp = int(oscvalue)
            # show a dot in console
            if DEBUG:
                print("%-51s|"%(" "*int(oscvalue/2)+".") )#, hr.hr,hr.hr_target)

        # wait for full highest value before pause
        if hr.paused:
            # TODO: Configurabel for fade up or fade out
            if hr.output_current == 100:
                hr.outputer.pause()




def server_callback(path, args, types, src):
    global hr
    print('osc path', path)
    print('osc args', args)
    if path == 'pause' and args[0] == 1:
        hr.pause()
    elif path == 'pause' and args[0] == 0:
        hr.unpause()
    elif path == 'int':
        hr.set(args[0])
    elif path == 'max':
        hr.out_max=min(100,float(args[0]))
    else:
        print("unknown path")
    # liblo.send(counter, path, args[0])

server.add_method(None, None, server_callback)


hr = HR()
if DEBUG:
    # in debug mode show info every 10 seconds
    info = Timer(10,lambda: print("info hr current: %d target: %d"%( hr.current,hr.target)))


server.start()
# keep the party going:
while 1:

    try:
        time.sleep(2)
        #r.set(220)
        time.sleep(50)
        # hr.set(50)
        # time.sleep(10)
        #hr.pause()
        #print("DONE DONE DONE")
    except KeyboardInterrupt:
        break

server.stop()
# pyplayer.terminate()
