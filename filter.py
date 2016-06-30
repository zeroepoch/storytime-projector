#!/usr/bin/env python3

import sys
import time
import struct

def emit_pre ():

    data  = b'W_Bit'

    sys.stdout.buffer.write(data)
    sys.stdout.flush()

    time.sleep(0.1)

    data  = b'MJPEG'
    data += struct.pack('<I', 12)
    data += struct.pack('<I', 0)
    data += struct.pack('<I', 2)

    sys.stdout.buffer.write(data)
    sys.stdout.buffer.write(data)
    sys.stdout.flush()

    time.sleep(0.1)

def emit_frame (frame, num):

    header  = b'MJPEG'
    header += struct.pack('<I', 12)
    header += struct.pack('<I', num)
    header += struct.pack('<I', len(frame))

    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(frame)
    sys.stdout.flush()

    time.sleep(0.083) # 12 fps

def main ():

    frame = bytes()
    frame_num = -1

    emit_pre()

    while True:

        data = sys.stdin.buffer.read(1024)
        if len(data) == 0:
            break

        start = data.find(b'\xff\xd8')
        if start < 0:
            frame += data
        else:

            frame += data[:start]

            if frame_num >= 0:
                assert frame[-2:] == b'\xff\xd9'
                emit_frame(frame, frame_num)
            frame_num += 1

            frame = data[start:]

    # TODO: handle last frame

main()

# vim: ai et ts=4 sts=4 sw=4
