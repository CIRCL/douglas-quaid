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

    def export_as_json(self):
        tmp_json = {}

        tmp_json["source"] = self.source.name

        return tmp_json
