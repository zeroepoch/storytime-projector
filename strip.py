#!/usr/bin/env python3
#
# Strips cruft between JPEG images
#

import os
import sys

# check arguments
if len(sys.argv) != 3:
    sys.stderr.write(
        "Usage: {} INPUT OUTPUT\n".format(os.path.basename(__file__)))
    sys.exit(1)

in_filename = sys.argv[1]
out_filename = sys.argv[2]

# open input file
try:
    in_file = open(in_filename, "rb")
except IOError:
    sys.stderr.write(
        "Error: Failed to read input file '{}'\n".format(in_filename))
    sys.exit(1)

# open output file
try:
    out_file = open(out_filename, "wb")
except IOError:
    sys.stderr.write(
        "Error: Failed to write output file '{}'\n".format(out_filename))
    sys.exit(1)

inside_image = False

# process input byte-by-byte
in_data = in_file.read(1)
while in_data:

    next_data = in_file.read(1)

    if not inside_image:

        # start of jpeg (ff d8)
        if (in_data == b'\xff') and (next_data == b'\xd8'):
            out_file.write(b'\xff\xd8')
            next_data = in_file.read(1)
            inside_image = True

    else:

        # end of jpeg (ff d9)
        if (in_data == b'\xff') and (next_data == b'\xd9'):
            out_file.write(b'\xff\xd9')
            next_data = in_file.read(1)
            inside_image = False

        # image byte
        else:
            out_file.write(in_data)

    in_data = next_data

# close files
in_file.close()
out_file.close()

# vim: ai et ts=4 sts=4 sw=4
