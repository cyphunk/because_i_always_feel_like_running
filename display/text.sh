#!/usr/bin/env bash
# base file as argument
source $(dirname $0)/configuration.sh

FILE=${1:-$BASE_DIR/media_player/media/whisper.txt}
WIDTH=${WIDTH:-25}
FONT=${FONT:-$FONTS/NimbusSans-Regular.otf-12.bdf}
SLEEP=${SLEEP:-9999}
COLOR=${COLOR:-255,255,255}
B=${B:-50}

IFS=$'\n'


( cat $FILE | fmt -w $WIDTH | head -2;
  sleep $SLEEP ) | eval  $BASE_DIR/libs/rpi-rgb-led-matrix/examples-api-use/text-example $MATRIXARGS \
-C $COLOR \
-b $B \
-f $FONT
