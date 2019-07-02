#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import logging
import os
import sys

# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))
FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')


class Edge:
    # Handle an edge of the graph

    def __init__(self, _from, _to, color="gray", label=None, value=None):
        self._from = _from
        self._to = _to

        self.color = color
        self.label = label
        self.value = value

    def update_member_id(self, old_id, new_id):
        # Modify an id in the list of members. Replace old by new.
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
    def load_from_dict(input):

        return Edge(_from=input["from"], _to=input["to"], color=input.get("color", ''),
                    label=input.get("label", None), value=input.get("value", None))

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' _from=', self._from, ' _to=', self._to, ' color=', self.color]))
