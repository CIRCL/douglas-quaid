#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import pathlib
import logging
import json
import base64

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


def save_picture(obj, file_path: pathlib.Path):
    # Save a bytes representation of a picture to a file

    logger = logging.getLogger()

    # Create parents if they does not exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("wb") as f:
        f.write(obj)

    logger.debug(f"File saved as {file_path}.")


def load_picture(file_path: pathlib.Path):
    # Return a bytes representation of a picture

    # Send the picture
    # rb = Open a file for reading only in binary format. Starts reading from beginning of file.
    with open(str(file_path), 'rb') as img:
        return img.read()
