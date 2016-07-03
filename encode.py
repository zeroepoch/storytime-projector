#!/usr/bin/env python3

import sys
import io
from PIL import Image

FRAME_WIDTH  = 320
FRAME_HEIGHT = 240
FRAME_SIZE   = FRAME_WIDTH * FRAME_HEIGHT * 4

while True:

    # read raw rgb data
    data_raw = sys.stdin.buffer.read(FRAME_SIZE)
    if len(data_raw) < FRAME_SIZE:
        break

    # load as pillow image
    img = Image.frombuffer(
        'RGB', (FRAME_WIDTH, FRAME_HEIGHT),
        data_raw, 'raw', 'BGRX', 0, 1
    )

    # compress as jpeg
    data_jpg = io.BytesIO()
    img.save(data_jpg, 'JPEG', quality=95)

    # write jpeg data
    sys.stdout.buffer.write(data_jpg.getbuffer())
    sys.stdout.flush()

# vim: ai et ts=4 sts=4 sw=4
