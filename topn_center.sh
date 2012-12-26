#!/bin/sh -x

xrandr --auto;

output=$(xrandr | grep \ connected | grep -v LVDS1 | cut -d " " -f1);

own_height=$(xrandr | grep \ connected | grep LVDS1 | cut -d "x" -f2 | cut -d+ -f1);
own_width=$(xrandr | grep \ connected | grep LVDS1 | cut -d " " -f3 | cut -dx -f1);

ext_height=$(xrandr | grep \ connected | grep -v LVDS1 | cut -d "x" -f2 | cut -d+ -f1);
ext_width=$(xrandr | grep \ connected | grep -v LVDS1 | cut -d " " -f3 | cut -dx -f1);

xrandr --output LVDS1 --pos $(( ( $ext_width - $own_width ) / 2 ))x$ext_height;

function add_1200p {
    mode=$(gtf 1920 1200 60 | grep -v "#" | sed 's/^ *//g' | grep -v "^\\s*\$" | cut -d" " -f2-)
    mode_name="$(echo "${mode}" | cut -d\" -f2)"
    xrandr --newmode $mode
    xrandr --addmode $output "${mode_name}"
    xrandr --output  $output --mode "${mode_name}"
}

function add_1080i {
    mode="$(gtf 1920 1080 60 | grep -v "#" | sed 's/^ *//g' | grep -v "^\\s*\$" | cut -d" " -f2-) interlaced"
    mode_name="$(echo "${mode}" | cut -d\" -f2)"
    xrandr --newmode $mode
}

