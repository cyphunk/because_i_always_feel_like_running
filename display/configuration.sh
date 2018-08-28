# configuration
# link to configuration.sh
MODIFIED=$(stat $0 | grep -i modify | awk '{print $2" "substr($3,1,5)}')

export MODEL_NAME="v1 ($MODIFIED)"
export IP="" # set to make static IP, else dhclient assumed
export CLIENT_SSID="MtElgon"
export CLIENT_PASSWORD="oguturunning"

export BASE_DIR="/home/pi/git/display"
export FONTS="$BASE_DIR/counter/ourfonts"
export UTILS="$BASE_DIR/libs/rpi-rgb-led-matrix/utils"

export BRIGHTNESS="10"

export MATRIXARGS='--led-gpio-mapping=adafruit-hat-pwm --led-rows 32 --led-cols 64 --led-pixel-mapper="S-Mapper;Rotate:90" --led-chain=6 --led-no-drop-privs --led-slowdown-gpio=2'
# --led-brightness works for some commands but others
# may have their own -b that then ignores that

# append _30000 for 33Hz compiled version
# append _25000 for 40Hz compiled version
# append _20000 for 50Hz compiled version
# append _10000 for 100Hz compiled version
# append _5000 for 200Hz compiled version
# append _0 for NoHz defined compiled version
export CMDIMAGE="$UTILS/led-image-viewer"
export CMDIMAGEARGS="-C"
export CMDVIDEO="$UTILS/video-viewer"
export CMDVIDEOARGS=""
export CMDCOUNT="$BASE_DIR/counter/counter"
export CMDCOUNTARGS="-d %H:%M:%S -C 255,0,0 -f $FONTS/SourceSansPro-Regular.otf-48.bdf -S -5 -y -10 -x -3 -s 9000"
export CMDTESTDISPLAY="$BASE_DIR/test_display.sh"
export CMDTEXT="$BASE_DIR/text.sh"
# cd libs; find . -exec touch {} \;
# #export FIXED_FRAME_MICROSECONDS=20000
# #export USER_DEFINES="-DFIXED_FRAME_MICROSECONDS=$FIXED_FRAME_MICROSECONDS"
#
# cd rpi-rgb-* && make && cd examples-* && make && cd ../utils && make && make video-viewer && cd ../..
#
# cd rpi-fb-* && make && cd ../..
#
# cd counter && make clean && make && cd ..
#
# IFS=" "; for f in ./libs/rpi-fb-matrix/display-test ./libs/rpi-fb-matrix/rpi-fb-matrix ./libs/rpi-rgb-led-matrix/examples-api-use/demo ./libs/rpi-rgb-led-matrix/examples-api-use/text-example ./libs/rpi-rgb-led-matrix/examples-api-use/minimal-example ./libs/rpi-rgb-led-matrix/examples-api-use/scrolling-text-example  ./libs/rpi-rgb-led-matrix/examples-api-use/clock ./libs/rpi-rgb-led-matrix/examples-api-use/c-example ./libs/rpi-rgb-led-matrix/examples-api-use/ledcat ./libs/rpi-rgb-led-matrix/led-matrix ./libs/rpi-rgb-led-matrix/utils/led-image-viewer ./libs/rpi-rgb-led-matrix/utils/video-viewer ./counter/counter; do echo cp $f ${f}_$FIXED_FRAME_MICROSECONDS; done; echo remove echo command manually and rerun
