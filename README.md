Code for counter "display", "cone" lights and "heartmonitor" components of
Ogutu Muraya's show 2018.08
... in progress


### 2022.12.06

Notes on display after years

The repo doesnt have all information
- https://github.com/cyphunk/because_i_always_feel_like_running

- Wifi: export CLIENT_SSID="MtElgon"
        export CLIENT_PASSWORD="oguturunning"
        IP given by router

Orientation

- Startup routines
  - crotating square, cross pattern, pacman, row,col, glow, text, counter
  - Row,column:
    On start you will see row,column descriptions show in bottom left. Example with default configuration.sh:

     panels when viwed from front
                 [  0,0] [  0,1] [  0,2] [  0,3] [  0,4] [  0,5] 
                 [     ] [     ] [     ] [     ] [     ] [     ]
                 [     ] [     ] [     ] [     ] [     ] [     ] 
                 [     ] [     ] [     ] [     ] [     ] [     ] <-- [ rpi ]

     panels when viewed from back
                 [  0,0] [  0,1] [  0,2] [  0,3] [  0,4] [  0,5] 
                 [     ] [     ] [     ] [     ] [     ] [     ]
                 [     ] [     ] [     ] [     ] [     ] [     ]
     [ rpi ] --> [     ] [     ] [     ] [     ] [     ] [     ]

     cables when viewed from back:
         i : in port 
         o : out port 
         ^ : ⮠ symbol 
         v : ⮦ symbol 
         * : power
                  .-----------.   .-----------.   . -----------.    
                  v           v   v           v   v           v    
                 [o    ] [    i] [o    ] [    i] [o    ] [    i]
                 [    ^] [     ] [     ] [     ] [     ] [     ]
                 [  *  ] [     ] [     ] [     ] [     ] [     ]
                 [     ] [     ] [     ] [     ] [     ] [     ]
                 [^    ] [     ] [     ] [     ] [     ] [     ]
     [ rpi ] --> [i    ] [    o] [i    ] [    o] [i    ] [     ]
                              ^   ^           ^   ^
                              '---'           '---'

configuration.sh
- Panel 6 first to pi (pi therefor on right,bottom when viewed from front (default)
  MATRIXARGS=--led-rows 32 --led-cols 64 --led-pixel-mapper="S-Mapper;Rotate:90" --led-chain=6
- Panel 0 first to pi (pi therefor on left, top?)


Login:


Power (assume 0.30EU per kWh):

measured with the In Btertekeware WBP 302737 power meter

- 08w still text on: 0.18kWh/day €0.06 - 1.3/w €0.4 - 05.8/m €1.75 - 070/y €21.04
- 10w pacmananimate: 0.24kWh/day €0.07 - 1.7/w €0.5 - 07.3/m €2.19 - 088/y €26.30 (or even the cross grid image)
- 18w running clock: 0.43kWh/day €0.13 - 3.0/d €0.9 - 13.2/w €3.95 - 158/y €47.34
   
### 2018.08.28 status

**Jitter** on brightness. RPi2 with image ``2017-09-07-raspbian-stretch-lite.zip`` has significantly less jitter than RPi3 with image ``2018-06-27-raspbian-stretch-lite.zip``. 
This is even after isolating user apps to 3 cores, disabling bluetooth, etc.

The fake Heart to OSC emulator works for demo purposes but could use 
improvements. I was working on trying to change it so that higher HR produces
a higher range of amplitude on the brightness. Also at the moment the 
HR brightness modulation only works in the counter.

**HDMI or VGA input**. We tried USB configurations which kinda work with
only slightly reduced quality (samples instagram) but causes entire system
to crash often after 5 minutes of use. Started working on integrating the 
avid hdmi to camera port attachment but currently wasn't getting any 
valid image.

In the future would like to see resolutions for 
* brightness modulation with 100% brightness.
* setup bluetooth HR
* hdmi input
* fadein/out media
