Issue

Intermentantly on the RPi 3 the panels will glitch for a few seconds.

Disabling Bluetooth and Wifi in /boot/config.txt does not help

This shows up when running demos or display test


Try this bootconfig which we know works on the rpi2

  # Uncomment some or all of these to enable the optional hardware interfaces
  dtparam=i2c_arm=on
  #dtparam=i2s=on
  dtparam=spi=on

  # Uncomment this to enable the lirc-rpi module
  #dtoverlay=lirc-rpi

  # Additional overlays and parameters are documented /boot/overlays/README

  # Enable audio (loads snd_bcm2835)
  dtparam=audio=off
  dtoverlay=i2c-rtc,ds1307

  root@raspberrypi:~# cat /etc/issue
  Raspbian GNU/Linux 9 \n \l
  root@raspberrypi:~# ls -l /etc/issue
  -rw-r--r-- 1 root root 27 Jul 27  2017 /etc/issue
  root@raspberrypi:~# uname -a
  Linux raspberrypi 4.9.41-v7+ #1023 SMP Tue Aug 8 16:00:15 BST 2017 armv7l GNU/Linux

  2017-09-07-raspbian-stretch-lite.zip

Compare with details from RPi3:

  2018-06-27-raspbian-stretch-lite.zip


Try this from the adafruit rgb-matrix.sh install script

       reconfig /boot/config.txt "^.*dtoverlay=i2c-rtc.*$" "dtoverlay=i2c-rtc,ds1307"
        apt-get -y remove fake-hwclock
        update-rc.d -f fake-hwclock remove
        sudo sed --in-place '/if \[ -e \/run\/systemd\/system \] ; then/,+2 s/^#*/#/' /lib/udev/hwclock-set

DID NOT HELP

Trying:
https://github.com/hzeller/rpi-rgb-led-matrix/issues/483

isolcpus=3 in cmdline.txt removes cpu4 from SMP (on user-space apps)
echo -1 > /proc/sys/kernel/sched_rt_runtime_us

then execute your app on that cpu:
NUSERS=4 taskset -c 3 ~pi/git/display/test_display.sh

ADDING THIS SOLVED IT:
--led-slowdown-gpio=2
removed:
/boot/config
dtoverlay=pi3-disable-wifi
dtoverlay=pi3-disable-bt
/boot/cmdline.txt
 isolcpus=3
