Code for counter "display", "cone" lights and "heartmonitor" components of
Ogutu Muraya's show 2018.08
... in progress


### 2018.08.28 status

**Jitter** on brightness. RPi2 with image ``2017-09-07-raspbian-stretch-lite.zip`` has significantly less jitter than RPi3 with image ``2018-06-27-raspbian-stretch-lite.zip``. 
This is even after isolating user apps to 3 cores, disabling bluetooth, etc.

The fake Heart to OSC emulator works for demo purposes but could use 
improvements. I was working on trying to change it so that higher HR produces
a higher range of amplitude on the brightness. Also at the moment the 
HR brightness modulation only works in the counter.

**HDMI or VGA input**. We tried USB configurations which kinda work with
only slightly reduced quality (samples instagram) but causes entire system
to crash often after 5 minutes of use. Started working on integrating the 
avid hdmi to camera port attachment but currently wasn't getting any 
valid image.

In the future would like to see resolutions for 
* brightness modulation with 100% brightness.
* setup bluetooth HR
* hdmi input
* fadein/out media
