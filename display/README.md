# Display

The display is a LED matrix __hardware__ currently of 192x64 pixels made of 6
64x32 panels connected to a Raspberry Pi. There are 3 different types of content
the system is configured currently to display which each have their own separate
software stacks: a __counter__, __media_player__ and experimental
__svideo_input__. The user chooses which content is show through the browser
based __ui__. Each of the content stacks accept OSC messages to change the
brightness of the display. A seperate Heart monitor is used to send OSC
messages.

The hardware is based mostly on Adafruit components, the display software is
based on [[[credit/link]]]




# Setup Requirements

For counter, media player, svideo input, on the RPi we install Henner Zeller [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix/) (tested at
commit 8189a56609eb87bcb1188201d07004186af1e17b) with the
S-Mapper [pull request](https://github.com/hzeller/rpi-rgb-led-matrix/pull/611),
and Adafruits [rpi-fb-matrix](https://github.com/hzeller/rpi-fb-matrix/) (tested
at commit 6d75622f0580fd73405201a70defd1d28c2a616a)

Prepare RPi:
  sudo apt-get update
  sudo apt-get -y install build-essential git libconfig++-dev
  sudo apt-get -y install libgraphicsmagick++1-dev libwebp-dev
  sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev
  sudo apt-get -y install liblo-dev #https://github.com/radarsat1/liblo/tree/e97ff7262894a36bb52335bdd1581a5198d8eb27 2014-01.27

  sudo apt-get -y install xawtv mplayer ffmpeg vlc x11-xserver-utils x11-apps xserver-xorg
  optional:
  sudo apt-get -y mencoder xterm fvwm omxplayer

Get libs:

  cd display/libs
  git clone https://github.com/hzeller/rpi-rgb-led-matrix/
  # we do not clone recursive here because currently this repo links to older
  # rpi-rgb-led-matrix and we need the newer tree support S-Mapper pull
  git clone https://github.com/hzeller/rpi-fb-matrix/

  cd rpi-rgb-led-matrix
  git fetch origin pull/611/head:pull_611 && git checkout pull_611

  cd ../rpi-fb-matrix
  rm -rf rpi-rgb-led-matrix
  ln -sf ../rpi-rgb-led-matrix .
  cd ..

Compile libs on RPi:

  Define DEFINES+=-DFIXED_FRAME_MICROSECONDS=10000 # 5000
  in lib/Makefile

  cd ~pi/git/display/libs/rpi-rgb-led-matrix
  make clean all
  cd utils
  make all
  make video-viewer
  cd ~pi/git/display/libs/rpi-fb-matrix
  make clean all

Configure libs and system:

  cat <<EOF > ~pi/git/display/libs/rpi-fb-matrix/matrix.cfg
    display_width = 64;
    display_height = 192;
    panel_width = 64;
    panel_height = 32;
    chain_length = 6;
    parallel_count = 1;
    panels = (
      ( { order = 0; rotate =   0; }),
      ( { order = 1; rotate =   180; }),
      ( { order = 2; rotate =   0; }),
      ( { order = 3; rotate =   180; }),
      ( { order = 4; rotate =   0; }),
      ( { order = 5; rotate =   180; })
    )
    crop_origin = (0,0)
EOF

  # Disable sound ('easy way' -- kernel module not blacklisted) edit or append
  set -- /boot/config.txt "^.*dtparam=audio.*$" "dtparam=audio=off"
  grep -q $2 $1 && sudo sed -i "s/$2/$3/g" $1 || (echo $3 | sudo tee -a $1)

  #Configure autologin and clear console for cleaner fb buffer:
  s raspi-config # set auto boot to pi user in console
  echo -en "setterm  -cursor off -foreground black -clear all | sudo tee /dev/tty1 >/dev/null" >> ~pi/.profile

Test:
  ~pi/git/display/libs/rpi-fb-matrix/display-test
  ~pi/git/display/test_display.sh
