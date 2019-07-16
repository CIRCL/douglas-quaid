#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import logging
import os
import sys
from typing import Dict
# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')


class Node_Meta:
    """
    Handle a serie of information related to the current node
    """

    def __init__(self):
        self.labels = []

    # ==================== Export / Import ====================

    def export_as_json(self):
        tmp_json = {}
        tmp_json["labels"] = self.labels
        return tmp_json

    @staticmethod
    def load_from_dict(input):
        tmp_meta = Node_Meta()
        tmp_meta.labels = input["labels"]
        return tmp_meta


class Node:
    """
    Handle a node of the graph
    """

    def __init__(self, label: str, id, image: str, metadata: Node_Meta = None):
        self.label = label
        self.id = id

        self.image = image  # Image path
        self.shape = "image"

        self.metadata = metadata

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_json = {}
        tmp_json["label"] = self.label
        tmp_json["id"] = self.id
        tmp_json["image"] = self.image
        tmp_json["shape"] = self.shape

        if self.metadata is not None :
            tmp_json["metadata"] = self.metadata.export_as_json()

        return tmp_json

    @staticmethod
    def load_from_dict(tmp_input : Dict):
        """
        Load/ Import a Node object from a dict
        :param tmp_input: A Dict version of the Node to import
        :return: The Node as an object
        """

        tmp_metadata = None
        if "metadata" in tmp_input.keys():
            tmp_metadata = Node_Meta.load_from_dict(tmp_input["metadata"])

        tmp_node = Node(label=tmp_input.get("label", ""), id=tmp_input["id"], image=tmp_input["image"], metadata=tmp_metadata)
        tmp_node.shape = tmp_input["shape"]

        return tmp_node

    def copy_ids_to_image(self):
        """
        Copy id value to image value
        :return: Nothing. Change internal state of the object
        """
        self.image = self.id

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' label=', self.label, ' id=', self.id, ' image=', self.image]))

