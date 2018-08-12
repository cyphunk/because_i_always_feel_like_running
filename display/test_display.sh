#!/usr/bin/env bash
# loop through some helpful test routines

cd $(dirname $0)

#loop the following until a user or N users logs into SSH
NUSERS=${NUSERS:-2} # set from cmdline for testing

ARGS='--led-gpio-mapping=adafruit-hat-pwm  --led-rows=32 --led-cols=64 --led-pixel-mapper="S-mapper;Rotate:90" --led-multiplexing=0 --led-chain=6 --led-slowdown-gpio=2'

DEMO="sudo ~pi/git/display/libs/rpi-rgb-led-matrix/examples-api-use/demo $ARGS"
TEST="sudo ~pi/git/display/libs/rpi-fb-matrix/display-test $ARGS"
TEXT="sudo ~pi/git/display/libs/rpi-rgb-led-matrix/examples-api-use/text-example -f ~pi/git/display/libs/rpi-rgb-led-matrix/fonts/6x9.bdf $ARGS"

while [ 1 ]; do
sleep 0.1
test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue # pause when user logged in

# Test orientation
eval $DEMO -t 6 -D 3 --led-brightness=100

test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue # pause when user logged
# Show numbers
eval timeout 6 $TEST --led-brightness=100

test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue # pause when user logged in

# Test pushing power
eval $DEMO -t 6 -D 4 --led-brightness=100

test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue # pause when user logged in

# show IP
test "$(cat /sys/class/net/eth0/operstate)" == "up" \
&& ETH0="$(ifconfig eth0 | grep inet | head -1 | awk '{print $2}') eth0\n"
test "$(cat /sys/class/net/wlan0/operstate)" == "up" \
&& WLAN="$(ifconfig wlan0 | grep inet | head -1 | awk '{print $2}') wlan0"
(echo -en "$ETH0$WLAN0" && sleep 6) | eval $TEXT

done

exit

# run through all demos
i=0;
while [ 1 ]; do
  echo $i;
  if [[ "$i" != "1" ]] && [[ "$i" != "2" ]]; then
  sudo ~pi/ledmatrix/rpi-rgb-led-matrix/examples-api-use/demo -t 20 -D $i -R 180 --led-rows 32 --led-cols 64 ~pi/ledmatrix/rpi-rgb-led-matrix/examples-api-use/runtext.ppm ;
  else
   sudo timeout 10 python test_count2.py
  fi

  i=$(($i+1));
  test $i -gt 11 && i=0;
done
