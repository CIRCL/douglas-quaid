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


class Edge:
    """
    Handle an edge of the graph
    """

    def __init__(self, _from: str, _to: str, color="gray", label: str = None, value=None):
        self._from: str = _from
        self._to: str = _to

        self.color: str = color
        self.label: str = label
        self.value: str = value

    def update_member_id(self, old_id, new_id):
        """
        Modify an id in the list of members. Replace old by new
        :param old_id: Old id to replace
        :param new_id: New id to replace to
        :return: Nothing, change internal state of the object only.
        """
        if self._from == old_id:
            self._from = new_id
        if self._to == old_id:
            self._to = new_id

    # ==================== Export / Import ====================

    def export_as_dict(self):
        tmp_json = {}

        tmp_json["from"] = self._from
        tmp_json["to"] = self._to
        tmp_json["color"] = self.color

        if self.label is not None:
            tmp_json["label"] = self.label
        if self.value is not None:
            tmp_json["value"] = self.value

        return tmp_json

    @staticmethod
    def load_from_dict(tmp_input : Dict):
        """
        Load/ Import a Edge object from a dict
        :param tmp_input: A Dict version of the Edge to import
        :return: The Edge as an object
        """

        return Edge(_from=tmp_input["from"],
                    _to=tmp_input["to"],
                    color=tmp_input.get("color", ''),
                    label=tmp_input.get("label", None),
                    value=tmp_input.get("value", None))

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' _from=', self._from, ' _to=', self._to, ' color=', self.color]))
