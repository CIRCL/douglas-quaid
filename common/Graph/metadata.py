#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
from typing import List
from enum import Enum, auto
import logging
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')


class Source(Enum):
    VISJS = auto()
    REDIS = auto()
    DBDUMP = auto()


class Metadata:
    # Handle metadata of the graph

    def __init__(self, source: Source):
        self.source = source

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_json = {}
        tmp_json["source"] = self.source.name
        return tmp_json

    @staticmethod
    def load_from_dict(input):

        if input["source"] == "VISJS" :
            tmp_source = Source.VISJS
        elif input["source"] == "REDIS" :
            tmp_source = Source.REDIS
        elif input["source"] == "DBDUMP" :
            tmp_source = Source.DBDUMP
        else :
            raise Exception("Incorrect Source in Metadata parsing")

        return Metadata(tmp_source)


