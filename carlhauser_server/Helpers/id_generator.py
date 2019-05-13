#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os, io
from PIL import Image
import hashlib
import pathlib
# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


def get_SHA1(file_value : io.BufferedReader): # TODO : Fix the input type
    # Get SHA1 hash from the file, directly in memory

    h  = hashlib.sha1()
    b  = bytearray(128*1024)
    mv = memoryview(b)

    for n in iter(lambda : file_value.readinto(mv), 0):
        h.update(mv[:n])

    return h.hexdigest()


def convert_to_bmp(file_value : io.BufferedReader):
    # Get SHA1 hash from the file, directly in memory

    curr_img = Image.open(file_value)
    with io.BytesIO() as output:
        curr_img.save(output, format="BMP")
        contents = output.getvalue()
        return contents

def write_to_file(file_value, file_path : pathlib.Path):
    # Write a buffer to a file. Works with convert_to_bmp() output
    newfile = open(str(file_path), 'wb')
    newfile.write(file_value)
    newfile.close()
