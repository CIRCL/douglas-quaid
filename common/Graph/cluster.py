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

from common.Graph import node


class Cluster(node.Node):
    # Handle a cluster of the graph

    def __init__(self, label: str, id, image: str):
        super().__init__(label, id, image)

        # For clusters only
        self.members = []
        self.group = ""


    def add_member_id(self, node_id):
        self.members.append(node_id)

    def get_nb_members(self):
        return len(self.members)

    def export_as_json(self):
        tmp_json = super().export_as_json()
        tmp_json["members"] = self.members
        tmp_json["group"] = self.group

        return tmp_json


