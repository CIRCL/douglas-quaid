#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import logging
import os
import sys

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

    def update_member_id(self, old_id, new_id):
        # Modify an id in the list of members. Replace old by new.
        if {old_id}.issubset(self.members):
            self.members.remove(old_id)
            self.members.add(new_id)

    # ==================== Request ====================

    def are_in_same_cluster(self, id_1, id_2):
        # Return True if both nodes id are in this cluster
        # TODO : make test !
        return {id_1, id_2}.issubset(self.members)

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_json = super().export_as_dict()
        tmp_json["members"] = sorted(list(self.members)) # Sorted to keep order, mainly for test purposes
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

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [super().get_str(), ' members=', list(self.members), ' group=', self.group]))

