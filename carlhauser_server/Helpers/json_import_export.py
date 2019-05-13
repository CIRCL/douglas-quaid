#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import pathlib
import logging
import json

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
import carlhauser_server.Configuration.template_conf as template_conf


class Custom_JSON_Encoder(json.JSONEncoder):
    '''
    Custom JSON Encoder to store Enum and custom configuration objects (for example) of the framework
    '''

    def default(self, o):
        if isinstance(o, pathlib.Path):
            return str(o)
        if isinstance(o, template_conf.JSON_parsable_Enum):
            # If this is an object flagger as String equivalent, parse it as a String
            return str(o)
        if isinstance(o, template_conf.JSON_parsable_Dict):
            # If this is an object flagged as dict equivalent, parse it as a dict.
            return o.__dict__
        return json.JSONEncoder.default(self, o)


def save_json(obj, file_path: pathlib.Path):
    # TODO : To fix json_data = ast.literal_eval(json_data) ?
    #  See : https://stackoverflow.com/questions/25707558/json-valueerror-expecting-property-name-line-1-column-2-char-1
    logger = logging.getLogger()

    # Create parents if they does not exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, cls=Custom_JSON_Encoder)

    logger.debug(f"File saved as {file_path}.")


def load_json(file_path: pathlib.Path):
    logger = logging.getLogger()
    # !! : json.load() is for loading a file. json.loads() works with strings.
    # json.loads will load a json string into a python dict, json.dumps will dump a python dict to a json string,

    if file_path.is_file():
        # We have a valid file to load
        with open(str(file_path.resolve())) as json_file:
            data = json.load(json_file)
        logger.debug(f"File loaded from {file_path}.")
    else:
        raise Exception(f"Cannot load the provided path to json : path is not a valid file {file_path}")

    return data
