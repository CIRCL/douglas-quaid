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


class Edge:
    # Handle an edge of the graph

    def __init__(self, _from, _to, color="gray"):
        self._from = _from
        self._to = _to

        self.color = color

    def export_as_json(self):
        tmp_json = {}

        tmp_json["from"] = self._from
        tmp_json["to"] = self._to
        tmp_json["color"] = self.color

        return tmp_json
