#!/bin/bash
# Fcking systemd calls rc.local very early
# so we added this to system d at end
# ./systemd/system/userstartup.service
# it is called as ROOT user

touch /home/pi/startup.sh.worked
# later rasbian images do not start ssh unless /boot/ssh file exists
# we start manually
echo "userstartup: SSH"
/etc/init.d/ssh start &

# don't wait for network on boot
test -e /etc/systemd/system/dhcpcd.service.d/wait.conf \
  && rm /etc/systemd/system/dhcpcd.service.d/wait.conf

# just in case dhcp not working
echo "userstartup: 10.0.0.1"
ifconfig eth0:1 10.0.0.1 &
# ping something for 2 minutes so engineer can find the ip by networking sniffing
ping -c 60 -i 2 -w 2 10.0.0.2 &


# install-info
echo "userstartup: INSTALL THINGS"
command -v rsync || dpkg -i ~pi/src/stretch/rsync_*_armhf.deb &
python -c 'import web' || dpkg -i ~pi/src/stretch/python-webpy_*.deb
python -c 'import pyinotify' || dpkg -i ~pi/src/stretch/python-pyinotify_*.deb
python -c 'import liblo' || dpkg -i ~pi/src/stretch/python-liblo_*.deb
test -e /usr/include/lo/lo.h || dpkg -i ~pi/src/stretch/liblo7_*.deb
# the dependency tree for avconv is too large. install src/* or apt-get it
#command -v avconv || dpkg -i src/*.deb

echo "userstartup: ENABLE THINGS"
#bash /home/pi/snippits/spi.sh

# rasbian now auto enlarges partition. pull back down so we can create fat
# for op1sync
# on workstation:
# s resize2fs /dev/mmcblk0p2 3G
# or use gparted


# Backet this part into a background shell so that if there is an error
# in the sourced configuration it does not cause the rest of the raspberry pi
# to crash
(
  source /home/pi/git/display/configuration.sh

  # settings suggested by rpi-rgb
  timedatectl set-ntp false
  systemctl stop cron
  #sudo apt-get remove bluez bluez-firmware pi-bluetooth triggerhappy pigpio

  echo "userstartup: WIFI"
  /home/pi/snippits/wifi_client.sh &

  echo "userstartup: start display test"
  /home/pi/git/display/test_display.sh &

  echo "userstartup: start web ui"
  python /home/pi/git/display/ui/server.py &

  echo "userstartup: start osc bridge "
  python /home/pi/git/display/counter/osc-hr-bridge.py &

) &

echo "userstartup: EXIT"

exit 0
