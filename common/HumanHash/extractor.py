#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib

from common.ImportExport.json_import_export import load_json


def extract(path: pathlib.Path):
    tmp_json = load_json(path)

    for val in tmp_json["values"]:
        for entry in val["entry"]:
            tmp_str = tmp_json["namespace"] + ":" + val["predicate"] + '="' + entry["value"] + '",'
            print(tmp_str)

if __name__ == '__main__':
    extract(pathlib.Path("./machinetag.json"))
