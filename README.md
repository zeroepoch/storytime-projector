# Storytime Projector

The Disney Storytime Theater Projector accepts a series of JPEG images in
JFIF format (aka MJPEG) that are `320x240` running at `12` fps. The script
provided records the desktop using FFMPEG and compresses the raw RGB frames
using the python library pillow into JPEG format (so they are in JFIF format).
Headers are prepended to the JPEG images and sent to the projector at
`192.168.10.1` on port `8888`.

First the string `W_Bit` is sent to wake up the device (I think?) and then 2
invalid headers are sent with the size field set to `2` to reset the image
sequence number (I think?). Images are then sent with an incrementing
sequence number starting at `0`. The frame header is formatted as follows
using mostly little endian 32-bit words:

| 5 Bytes | 4 Bytes | 4 Bytes | 4 Bytes    | N+ Bytes   |
|---------|---------|---------|------------|------------|
| MJPEG   | 12      | Seq Num | Image Size | JPEG Image |

To project your Linux desktop, first install ffmpeg and python3-pillow, then
just run the following script while connected to the projector WiFi network:

```
./project.py
```
