#!/usr/bin/env bash
# loop through some helpful test routines
# This is a misnomer. This is the main display script

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

function network_enabled () {
    test "$(cat /sys/class/net/eth0/operstate)" == "up" \
    && ETH0="$(ifconfig eth0 | grep 'inet ' | head -1 | awk '{print $2}')"
    test "$(cat /sys/class/net/wlan0/operstate)" == "up" \
    && WLAN0="$(ifconfig wlan0 | grep 'inet ' | head -1 | awk '{print $2}')"
    SSID=$(/sbin/iwconfig 2>/dev/null  | grep -i ssid | sed -e 's/.*SSID: *"\([^"]*\)".*/\1/')
    test -n "$WLAN0$ETH0" && NETWORKUP=1 || NETWORKUP=0
    (
      (
          echo -e "network:"
          test -n "$ETH0" && echo  "eth0  $ETH0"
          test -n "$WLAN0" && echo "wlan0 $WLAN0"
          test -n "$SSID" && echo  "ssid  $SSID"
          sleep 5
      ) | eval $TEXT
    ) &
    child=$!
    wait "$child"  
    echo $NETWORKUP 
}

# Do test loop until network is up or max 3 times
count=0
while [ 1 ]; do
  sleep 0.1
  count=$(($count+1))

  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # Show Test orientation pattern. 
  # must be inside eval, else $! = evals shell
  eval "$DEMO -t 6 -D 3 --led-brightness=100 &"
  child=$!
  wait "$child"

  # pause when user logged in so user can run tests without collisions which crashes system
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # Show display index numbers (0,1 0,2 etc)
  eval "timeout 6 $TEST --led-brightness=100 &"
  child=$!
  wait "$child"
  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # show IP
  NETWORKUP=$(network_enabled)
  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # Show cube
  eval "$DEMO -t 8 -D 0 --led-brightness=75 &"
  child=$!
  wait "$child"
  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # Test pushing power
  eval "$DEMO -t 10 -D 4 --led-brightness=100 &"
  child=$!
  wait "$child"
  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # show IP
  NETWORKUP=$(network_enabled)

  # If this is the 2nd time through, and network is already up, 
  # then stop display testing loop
  test $NETWORKUP -eq 1 -a $count -gt 2 && break

  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

done

# Now run main routines
echo "start main routine"

count=0
while [ 1 ]; do
  sleep 0.1
  count=$(($count+1))
  # break when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # Show image
  eval "timeout 120 $CMDIMAGE $CMDIMAGEARGS $MATRIXARGS --led-brightness=75 ./media_player/media/Flag_of_Palestine.png &"
  child=$!
  wait "$child"
  # pause when user logged in
  test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

  # Show counter
  set -x
  # set to 99 brightness if you want to make dimmable
  eval "timeout 60 $CMDCOUNT $MATRIXARGS -d %M:%S -m 1 -C 255,0,0 -f /home/pi/git/display/counter/ourfonts/SourceSansPro-Regular.otf-56.bdf -b 100 -S -6 -y -18 -x -3 -s 9000 &"
  child=$!
  set +x
  wait "$child"

  # Iterate through ogutu's text
  # obt do the first 6 parts
  last=$(ls $BASE_DIR/media_player/media/whisper_25_*|head -6|wc -l)
  fcount=0
  for f in `ls $BASE_DIR/media_player/media/whisper_25_*| head -6`; do
    # break when user logged in
    test $(w --short --no-header|wc -l) -ge ${NUSERS} && continue 

    fcount=$(($fcount+1))
    # sleep longer on last phrase
    if test $fcount -lt $last; then
      nwords=$(cat $f | wc -w)
      SLEEP=$(($nwords/2)) 
      test $SLEEP -ge 3 || SLEEP=3
    else
      SLEEP=10
    fi
    export SLEEP
    echo words $nwords sleep $SLEEP $f
    $BASE_DIR/text.sh $f
  done

done

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
