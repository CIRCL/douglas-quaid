#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import io

from PIL import Image

from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


def get_SHA1(file_value: io.BufferedReader):
    """
    Get SHA1 hash of the file, directly in memory
    TODO : Fix the input type
    :param file_value: A file to compute the SHA-1
    :return: the SHA-1 of the file in memory
    """

    h = hashlib.sha1()
    b = bytearray(128 * 1024)
    mv = memoryview(b)

    for n in iter(lambda: file_value.readinto(mv), 0):
        h.update(mv[:n])

    return h.hexdigest()


def convert_to_bmp(file_value: io.BufferedReader):
    """
    Get the BMP version of the file, directly in memory
    :param file_value: A file to compute the BMP version
    :return: the BMP version of the file
    """

    curr_img = Image.open(file_value)
    with io.BytesIO() as output:
        curr_img.save(output, format="BMP")
        contents = output.getvalue()
        return contents


'''
def write_to_file(file_value, file_path: pathlib.Path):
    """
    Write a picture to a file
    :param file_value: A file to compute the save
    :param file_path: the path where the file will be saved
    :return: nothing
    """
    # Write a buffer to a file. Works with convert_to_bmp() output
    newfile = open(str(file_path), 'wb')
    newfile.write(file_value)
    newfile.close()
'''
