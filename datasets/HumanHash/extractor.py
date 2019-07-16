#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging.config
import pathlib

def extract(path: pathlib.Path):
    tmp_json = load_json(path)

    for val in tmp_json["values"]:
        for entry in val["entry"]:
            tmp_str = tmp_json["namespace"] + ":" + val["predicate"] + '="' + entry["value"] + '",'
            print(tmp_str)


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


if __name__ == '__main__':
    extract(pathlib.Path("./machinetag.json"))
