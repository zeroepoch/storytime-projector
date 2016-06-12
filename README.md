# Storytime Projector

```
ffmpeg -loglevel quiet -video_size $(xdpyinfo | awk '/dimensions:/{print $2}') -framerate 12 -f x11grab -i :0.0 -vf scale=320:240 -f mjpeg -q 10 - | ./filter.py | nc 192.168.10.1 8888
```
