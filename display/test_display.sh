#!/usr/bin/env bash
# loop through some helpful test routines

cd $(dirname $0)
source configuration.sh

#loop the following until a user or N users logs into SSH
NUSERS=${NUSERS:-2} # set from cmdline for testing

DEMO="$BASE_DIR/libs/rpi-rgb-led-matrix/examples-api-use/demo $MATRIXARGS"
TEST="$BASE_DIR/libs/rpi-fb-matrix/display-test $MATRIXARGS"
TEXT="$BASE_DIR/libs/rpi-rgb-led-matrix/examples-api-use/text-example -f $BASE_DIR/libs/rpi-rgb-led-matrix/fonts/6x9.bdf $MATRIXARGS"


_term() {
  echo "Caught SIGTERM/SIGINT(ctrl+c) signal!"
  /bin/ps aux | grep "$child " | grep -v grep
  kill -TERM "$child" 2>/dev/null
  # damnit, the various bashes for the text example wont die easily
  #kill -TERM $(pgrep -f test_display.sh)
  test -z "$(pgrep sleep)" || kill -TERM $(pgrep sleep)
  exit
}

trap _term SIGTERM SIGINT

while [ 1 ]; do
  sleep 0.1
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue # pause when user logged in

  # Test orientation. & must be inside eval, else $! = evals shell
  eval "$DEMO -t 6 -D 3 --led-brightness=100 &"
  child=$!
  wait "$child"

  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue

  # Show numbers
  eval "timeout 6 $TEST --led-brightness=100 &"
  child=$!
  wait "$child"

  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue

  # show IP
  test "$(cat /sys/class/net/eth0/operstate)" == "up" \
  && ETH0="$(ifconfig eth0 | grep 'inet ' | head -1 | awk '{print $2}') eth0\n"
  test "$(cat /sys/class/net/wlan0/operstate)" == "up" \
  && WLAN0="$(ifconfig wlan0 | grep 'inet ' | head -1 | awk '{print $2}') wlan0\n"
  ( (echo -en "network:\n$ETH0$WLAN0" && sleep 6) | eval $TEXT ) &
  child=$!
  wait "$child"

  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue

  # Test pushing power
  eval "$DEMO -t 10 -D 4 --led-brightness=100 &"
  child=$!
  wait "$child"


  done
exit

# run through all demos
# i=0;
# while [ 1 ]; do
#   echo $i;
#   if [[ "$i" != "1" ]] && [[ "$i" != "2" ]]; then
#   sudo ~pi/ledmatrix/rpi-rgb-led-matrix/examples-api-use/demo -t 20 -D $i -R 180 --led-rows 32 --led-cols 64 ~pi/ledmatrix/rpi-rgb-led-matrix/examples-api-use/runtext.ppm ;
#   else
#    sudo timeout 10 python test_count2.py
#   fi
#
#   i=$(($i+1));
#   test $i -gt 11 && i=0;
# done
