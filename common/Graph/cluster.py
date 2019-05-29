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
        self.members = set()
        self.group = ""

    def add_member_id(self, node_id):
        self.members.add(node_id)

    def get_nb_members(self):
        return len(self.members)

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_json = super().export_as_dict()
        tmp_json["members"] = self.members
        tmp_json["group"] = self.group

        return tmp_json

    @staticmethod
    def create_from_parent(parent : node.Node):
        return Cluster(label=parent.label, id=parent.id, image=parent.image)

    @staticmethod
    def load_from_dict(input):
        tmp_cluster = Cluster.create_from_parent(node.Node.load_from_dict(input))

        for m in input["members"]:
            tmp_cluster.add_member_id(m)

        tmp_cluster.group = input["group"]

        return tmp_cluster