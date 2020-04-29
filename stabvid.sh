#!/bin/bash
if [[ "$1" == "" || "$1" == "help" ]]; then
    echo "Usage: `basename $0` filename" >&2
    # Error message to stderr.
    exit $E_NOARGS
    # Returns 85 as exit status of script (error code).
fi

if [ ! -f "$1" ]; then
    echo "Error: Selected file ($1) is missing"
    exit
fi

if [[ "$1" != *.* ]]; then
    echo "Error: File has no extension (example.mkv)"
    exit
fi

FILE=$1
FILE_BASE=`echo -n "$1" | cut -d "." -f 1 -`
FILE_TRF=$FILE_BASE".trf"
FILE_OUT=$FILE_BASE"-stab.mkv"
echo "Processing file:"
echo -e "\t input file: "$FILE
echo -e "\t pass 1 file: "$FILE_TRF
echo -e "\t output file: "$FILE_OUT

sleep 2

ffmpeg -i $FILE -vf vidstabdetect=shakiness=10:accuracy=15:result="$FILE_TRF" \
    -f null -
ffmpeg -i $FILE -vf vidstabtransform=input="$FILE_TRF",unsharp=5:5:0.8:3:3:0.4 \
    -c:v libx264 -crf 16 -c:a copy -preset fast $FILE_OUT
