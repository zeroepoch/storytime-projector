#!/usr/bin/env python3

import sys
import struct

def emit_pre ():

    out  = b'W_Bit'
    out += b'MJPEG'
    out += struct.pack('<I', 12)
    out += struct.pack('<I', 0)
    out += struct.pack('<I', 0)

    sys.stdout.buffer.write(out)

def emit_frame (frame, num):

    header  = b'MJPEG'
    header += struct.pack('<I', 12)
    header += struct.pack('<I', num)
    header += struct.pack('<I', len(frame))

    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(frame)

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

main()

# vim: ai et ts=4 sts=4 sw=4
