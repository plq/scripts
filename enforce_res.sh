#!/bin/bash

usage() {
    echo "usage $0 <out> <w> <h> [refresh]"
}

if [ -z "$3" ]; then
    usage;
    exit 1;

elif [ -z "$4" ]; then
    out=$1
    w=$2
    h=$3
    r=60

elif [ -z "$5" ]; then
    out=$1
    w=$2
    h=$3
    r=$4

fi


if ! xrandr | grep -q ^$out; then
    echo Display $out not found.
    usage;
    xrandr --listmonitors
    exit 1;
fi;

set -x

modename=$(cvt $w $h $r | grep -v ^\# | cut -d\" -f 2)

xrandr --newmode $modename $(cvt $w $h $r | grep -v ^\# | cut -d" " -f 3-)
xrandr --addmode $out $modename
xrandr --output $out --auto
xrandr --output $out --mode $modename
