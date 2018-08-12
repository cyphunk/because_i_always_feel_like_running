#!/usr/bin/env bash
[ $# -le 0 ] && echo "$0 <ip>" && exit 1
#IP=192.168.4.1
IP=$1
EXCLUDEFLAGS="
--exclude media_selected.txt
--exclude __pycache__
--exclude *.pyc
--exclude sync.sh --exclude sync_back.sh
"
echo "## START TEST"
rsync -avzn $EXCLUDEFLAGS -e ssh root@${IP}:/home/pi/show_v3/ .
echo "## END TEST"
read -p "continue syncing? (ctrl+c exit if not) "
set -x
rsync -avz $EXCLUDEFLAGS -e ssh root@${IP}:/home/pi/show_v3/ .
set +x
