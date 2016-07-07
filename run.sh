#!/bin/sh
ffmpeg -loglevel quiet -video_size $(xdpyinfo | awk '/dimensions:/{print $2}') -framerate 12 -f x11grab -i :0.0 -vf scale=320x240 -f rawvideo - | ./encode.py | ./filter.py | nc --send-only 192.168.10.1 8888
