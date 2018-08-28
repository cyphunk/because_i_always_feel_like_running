#!/usr/bin/env bash

cd media
IFS=$'\n'; i=`printf "%03d" 1`; for line in `cat whisper.txt`; do echo $line | fmt -w 25 > whisper_25_`printf "%03d" ${i}`.txt; i=$(($i+1)); done
