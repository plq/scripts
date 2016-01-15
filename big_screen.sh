if [ -n "$(xrandr | grep HDMI-1-0)" ]; then
    HDMI=HDMI-1-0
    LVDS=LVDS-1-0
else
    LVDS=LVDS1
    HDMI=HDMI1
fi

xrandr --newmode $(cvt 2560 1440 30 | grep -v ^\# | cut -b 10-)
xrandr --addmode $HDMI $(cvt 2560 1440 30 | grep -v ^\# | cut -d " " -f 2)
xrandr --output $HDMI --mode $(cvt 2560 1440 30 | grep -v ^\# | cut -d " " -f 2)

if [ -z "$1" ]; then
    SCREEN_STATE="--off"
else
    SCREEN_STATE="$1 $HDMI"
fi

xrandr --output $LVDS $SCREEN_STATE
