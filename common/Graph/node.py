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


class Node_Meta:
    # Handle a serie of information related to the current node

    def __init__(self):
        self.labels = []

    def export_as_json(self):
        tmp_json = {}
        tmp_json["labels"] = self.labels
        return tmp_json


class Node:
    # Handle a node of the graph

    def __init__(self, label: str, id, image: str, metadata: Node_Meta = None):
        self.label = label
        self.id = id

        self.image = image  # Image path
        self.shape = "image"

        self.metadata = metadata

    def export_as_json(self):
        tmp_json = {}
        tmp_json["label"] = self.label
        tmp_json["id"] = self.id
        tmp_json["image"] = self.image
        tmp_json["shape"] = self.shape

        if self.metadata is not None :
            tmp_json["metadata"] = self.metadata.export_as_json()

        return tmp_json
