# Storytime Projector

JPEG frames must have JIFF header (TODO: compress frames from ffmpeg myself)

```
ffmpeg -loglevel quiet -video_size $(xdpyinfo | awk '/dimensions:/{print $2}') -framerate 12 -f x11grab -i :0.0 -vf scale=320x240 -f mjpeg -q 10 - | ./filter.py | nc --send-only 192.168.10.1 8888
```

```
ffmpeg -t 5 -video_size $(xdpyinfo | awk '/dimensions:/{print $2}') -framerate 1 -f x11grab -i :0.0 -vf scale=320x240 -f rawvideo test.raw
```
