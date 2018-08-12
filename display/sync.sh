#!/usr/bin/env bash
# sync files to target pi
EXCLUDEFLAGS="
--exclude __pycache__
--exclude *.pyc
"
[ $# -le 0 ] && echo "$0 <ip>" && exit 1
IP=$1
set -x
rsync -avz $EXCLUDEFLAGS -e ssh ./ pi@${IP}:/home/pi/git/display/
set +x
