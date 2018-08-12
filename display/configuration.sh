# configuration
# link to configuration.sh
MODIFIED=$(stat $0 | grep -i modify | awk '{print $2" "substr($3,1,5)}')

export MODEL_NAME="v1 ($MODIFIED)"
export IP="" # set to make static IP, else dhclient assumed
export CLIENT_SSID="MtElgon"
export CLIENT_PASSWORD="ogutu"

export MATRIXARGS='--led-gpio-mapping=adafruit-hat-pwm --led-rows 32 --led-cols 64 --led-pixel-mapper="S-Mapper;Rotate:90" --led-chain=6 --led-no-drop-privs --led-slowdown-gpio=2'
export CMDIMAGE="/home/pi/git/display/libs/rpi-rgb-led-matrix/utils/led-image-viewer"
export CMDIMAGEARGS="-C"
export CMDVIDEO="/home/pi/git/display/libs/rpi-rgb-led-matrix/utils/video-viewer"
export CMDVIDEOARGS=""
export CMDCOUNT="/home/pi/git/display/counter/counter"
export CMDCOUNTARGS="-d %M:%S -m 2 -C 255,0,0 -f /home/pi/git/display/counter/ourfonts/SourceSansPro-Regular.otf-46.bdf -y -8 -x -2 -S -4"
export CMDTESTDISPLAY="/home/pi/git/display/test_display.sh"
