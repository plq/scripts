xrandr --newmode $(cvt 2560 1440 30 | grep -v ^\# | cut -b 10-)
xrandr --addmode HDMI1 $(cvt 2560 1440 30 | grep -v ^\# | cut -d " " -f 2)
xrandr --output HDMI1 --mode $(cvt 2560 1440 30 | grep -v ^\# | cut -d " " -f 2)

if [ -z "$1" ]; then
    SCREEN_STATE="--off"
else
    SCREEN_STATE="$1 HDMI1"
fi

xrandr --output LVDS1 $SCREEN_STATE
