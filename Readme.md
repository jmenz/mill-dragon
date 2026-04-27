INIT


TOUCH:
sudo apt install evtest

dev name:
ILITEK ILITEK-TP


sudo apt install libinput-bin libinput-tools xserver-xorg-input-libinput

sudo nano /etc/X11/xorg.conf.d/99-libinput-touch.conf
***
Section "InputClass"
    Identifier "Ilitek Touchscreen Native"
    MatchProduct "ILITEK ILITEK-TP"
    MatchDevicePath "/dev/input/event*"
    Driver "libinput"

    Option "Accept" "on"
    Option "MatchIsPointer" "off"
    Option "MatchIsTouchscreen" "on"

    Option "Mode" "Absolute"
    Option "AccelerationProfile" "-1"
    Option "AccelerationScheme" "none"
    Option "AccelSpeed" "-1"

    Option "Tapping" "on"
    Option "TappingButtonMap" "lrm"
EndSection
*** 

sudo apt install unclutter-xfixes
unclutter --hide-on-touch

testing:

xinput test-xi2 [8]

sudo libinput debug-events

libinput-gestures -d

echo $XDG_SESSION_TYPE




QT_XCB_NO_XI2=1 linuxcnc