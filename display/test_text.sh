#!/usr/bin/env bash

source $(dirname $0)/configuration.sh
FILE=${FILE:-$BASE_DIR/media_player/media/whisper.txt}
WIDTH=${WIDTH:-45}
FONT=${FONT:-$FONTS/NimbusSans-Regular.otf-8.bdf}
SLEEP=${SLEEP:-6.5}
COLOR=${COLOR:-255,255,255}
B=${B:-50}

IFS=$'\n'
set -x

( for l in `cat $FILE | fmt -w $WIDTH` ; do
  echo "$l";
  sleep $SLEEP;
done) | eval  $BASE_DIR/libs/rpi-rgb-led-matrix/examples-api-use/text-example $MATRIXARGS \
-C $COLOR \
-b $B \
-f $FONT
