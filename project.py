#!/usr/bin/env python3

import sys, io
import time
import struct
import subprocess

# TODO: check for PIL lib

import PIL.Image

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_RATE = 12

HOST_ADDR = "192.168.10.1"
HOST_PORT = 8888


# read/write stream exception
class StreamError (Exception):
    pass


# ffmpeg pipe for streaming desktop as jpeg images
class DesktopStream:

    # constructor
    def __init__ (self, width, height, rate):

        self.frame_width = width
        self.frame_height = height
        self.frame_size = width * height * 4

        # TODO: check for programs

        # get display resolution
        display_res = subprocess.check_output(
            "xdpyinfo | awk '/dimensions:/{print $2}'",
            shell=True).decode().strip()

        # build ffmpeg command line
        cmd_line  = "ffmpeg"
        cmd_line += " -loglevel quiet"  # no stderr
        cmd_line += " -video_size {0}".format(display_res)
        cmd_line += " -framerate {0}".format(rate)
        cmd_line += " -f x11grab -i :0.0"
        cmd_line += " -vf scale={0}x{1}".format(width, height)
        cmd_line += " -f rawvideo -"

        # open input video stream
        self.input = subprocess.Popen(
            cmd_line.split(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)

    # terminate video stream
    def close (self):

        # close input video stream
        self.input.terminate()

    # get jpeg desktop image
    def get_jpeg (self):

        # read raw rgb data
        data_rgb = self.input.stdout.read(self.frame_size)
        if len(data_rgb) < self.frame_size:
            raise StreamError

        # load as pillow image
        img = PIL.Image.frombytes(
            'RGB', (self.frame_width, self.frame_height),
            data_rgb, 'raw', 'BGRX', 0, 1)

        # compress as jpeg
        data_jpg = io.BytesIO()
        img.save(data_jpg, 'JPEG', quality=95)

        return data_jpg.getvalue()


# network connection for formatting output to projector
class ProjectorStream:

    # constructor
    def __init__ (self, addr, port):

        self.host_addr = addr
        self.host_port = port
        self.frame_num = 0

        # TODO: deal with socket

        # prepare projector
        self.send_preamble()

    # close network connection
    def close (self):
        pass

    # initialize projector connection
    def send_preamble (self):

        # wake up projector
        data  = b'W_Bit'
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

        time.sleep(0.1)

        # reset sequence numbers
        data  = b'MJPEG'
        data += struct.pack('<I', 12)
        data += struct.pack('<I', 0)
        data += struct.pack('<I', 2)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

        time.sleep(0.1)

    # send formatted frame data
    def send_frame (self, data):

        # prepare frame header
        header  = b'MJPEG'
        header += struct.pack('<I', 12)
        header += struct.pack('<I', self.frame_num)
        header += struct.pack('<I', len(data))

        # send header and image
        sys.stdout.buffer.write(header)
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

        self.frame_num += 1


# entry point
def main ():

    # create streams
    projector = ProjectorStream(HOST_ADDR, HOST_PORT)
    desktop = DesktopStream(FRAME_WIDTH, FRAME_HEIGHT, FRAME_RATE)

    try:
        # project desktop
        while True:
            frame = desktop.get_jpeg()
            projector.send_frame(frame)
    except (StreamError, KeyboardInterrupt):
        pass

    # terminate streams
    desktop.close()
    projector.close()

if __name__ == "__main__":
    main()

# vim: ai et ts=4 sts=4 sw=4
