#!/usr/bin/env python3

import sys
import shutil
import subprocess
import io
import socket
import struct
import time

try:
    # load pillow library
    import PIL.Image
except ImportError:
    sys.stderr.write("Error: Missing package 'python3-pillow'\n")
    sys.exit(1)


FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_RATE = 12

HOST_ADDR = "192.168.10.1"
HOST_PORT = 8888


# desktop pipe from ffmpeg underflow
class DesktopPipeUnderflow (Exception):
    pass

# desktop pipe programs missing
class DesktopProgramMissing (Exception):
    def __init__ (self, name):
        self.program_name = name


# ffmpeg pipe for streaming desktop as jpeg images
class DesktopStream:

    # constructor
    def __init__ (self, width, height, rate):

        self.frame_width = width
        self.frame_height = height

        # check programs exist
        if not shutil.which("xdpyinfo"):
            raise DesktopProgramMissing("xdpyinfo")
        if not shutil.which("ffmpeg"):
            raise DesktopProgramMissing("ffmpeg")

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

        # pixel = B(8bit) + G(8bit) + R(8bit) + X(0xff)
        frame_size = self.frame_width * self.frame_height * 4

        # read raw rgb data
        data_rgb = self.input.stdout.read(frame_size)
        if len(data_rgb) < frame_size:
            raise DesktopPipeUnderflow

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

        self.frame_num = 0

        # open network connection
        self.output = socket.socket()
        self.output.settimeout(10)
        self.output.connect((addr, port))
        self.output.setblocking(False)

        # prepare projector
        self._send_preamble()

    # close projector connection
    def close (self):

        # close output network stream
        self.output.close()

    # initialize projector connection
    def _send_preamble (self):

        # wake up projector
        data  = b'W_Bit'
        self.output.send(data)

        time.sleep(0.2)

        # reset sequence numbers
        data  = b'MJPEG'
        data += struct.pack('<I', 12)
        data += struct.pack('<I', 0)
        data += struct.pack('<I', 2)
        self.output.send(data)
        self.output.send(data)

        time.sleep(0.1)

    # send formatted frame data
    def send_frame (self, data):

        # prepare frame header
        header  = b'MJPEG'
        header += struct.pack('<I', 12)
        header += struct.pack('<I', self.frame_num)
        header += struct.pack('<I', len(data))

        # send header and image
        self.output.send(header)
        self.output.send(data)

        # empty input buffer
        try:
            self.output.recv(1024)
        except BlockingIOError:
            pass

        self.frame_num += 1


# entry point
def main ():

    try:
        # create projector stream
        projector = ProjectorStream(HOST_ADDR, HOST_PORT)
    except (socket.timeout, ConnectionRefusedError):
        sys.stderr.write(
            "Error: Failure connecting to '{0}:{1}'\n".format(
            HOST_ADDR, HOST_PORT))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

    try:
        # create desktop stream
        desktop = DesktopStream(FRAME_WIDTH, FRAME_HEIGHT, FRAME_RATE)
    except DesktopProgramMissing as e:
        sys.stderr.write(
            "Error: Missing program '{0}' in $PATH\n".format(
            e.program_name))
        projector.close()
        sys.exit(1)

    print("Streaming desktop to projector...")

    try:
        # project desktop
        while True:
            frame = desktop.get_jpeg()
            projector.send_frame(frame)
    except DesktopPipeUnderflow:
        sys.stderr.write(
            "Warning: Failure capturing desktop from FFMPEG\n")
    except (BrokenPipeError, ConnectionResetError):
        sys.stderr.write(
            "Warning: Connection to projector was broken\n")
    except KeyboardInterrupt:
        pass

    # terminate streams
    desktop.close()
    projector.close()

    print("Desktop streaming terminated")


if __name__ == "__main__":
    main()

# vim: ai et ts=4 sts=4 sw=4
