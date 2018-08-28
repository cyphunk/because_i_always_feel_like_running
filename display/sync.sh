#!/usr/bin/env bash
# sync files to target pi
EXCLUDEFLAGS="
--exclude __pycache__
--exclude *.pyc
--exclude counter/counter
--exclude osc-send
--exclude osc-send.o
--exclude counter.o
"
[ $# -le 0 ] && echo "$0 <ip>" && exit 1
IP=$1
set -x
rsync -ravz $EXCLUDEFLAGS -e ssh ./ pi@${IP}:/home/pi/git/display/
set +x
