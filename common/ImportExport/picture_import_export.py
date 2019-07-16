#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import pathlib

from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


def save_picture(obj, file_path: pathlib.Path):
    """
    Save a bytes representation of a picture to a file
    :param obj: Object to save (is a picture)
    :param file_path: path to which the object should be saved
    :return: Nothing
    """

    logger = logging.getLogger()

    # Create parents if they does not exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("wb") as f:
        f.write(obj)

    logger.debug(f"File saved as {file_path}.")


def load_picture(file_path: pathlib.Path):
    """
    Return a bytes representation of a picture
    :param file_path: the path of the picture to load
    :return: The loaded picture
    """

    # Send the picture
    # rb = Open a file for reading only in binary format. Starts reading from beginning of file.
    with open(str(file_path), 'rb') as img:
        return img.read()
