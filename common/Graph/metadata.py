#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum, auto
from typing import Dict

from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class Source(Enum):
    VISJS = auto()
    REDIS = auto()
    DBDUMP = auto()


class Metadata:
    """
    Handle metadata of the graph
    """

    def __init__(self, source: Source):
        self.source = source

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_json = {}
        tmp_json["source"] = self.source.name
        return tmp_json

    @staticmethod
    def load_from_dict(tmp_input: Dict):
        """
        Load/ Import a Meta object from a dict
        :param tmp_input: A Dict version of the Meta to import
        :return: The Meta as an object
        """

        if tmp_input["source"] == "VISJS":
            tmp_source = Source.VISJS
        elif tmp_input["source"] == "REDIS":
            tmp_source = Source.REDIS
        elif tmp_input["source"] == "DBDUMP":
            tmp_source = Source.DBDUMP
        else:
            raise Exception("Incorrect Source in Metadata parsing")

        return Metadata(tmp_source)
