# -*- coding: utf-8 -*-

import logging
import unittest

from common.HumanHash.dataturks_graph import DataturksGraph


class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.base_folder = pathlib.Path("./HumanHash/HumanHash").resolve()
        tmp_instance = DataturksGraph()

    def test_strip_tag_normal(self):
        stripped = DataturksGraph.strip_tag('dark - web: structure = "legal-statement"')
        self.assertEqual(stripped, "legal-statement")

    def test_strip_tag_no_to_parse(self):
        stripped = DataturksGraph.strip_tag("to_delete")
        self.assertEqual(stripped, "to_delete")

    def test_create_set_from_labels_list(self):
        set, key = DataturksGraph.create_set_from_labels_list(['dark - web: structure = "legal-statement"', "to_delete"])
        self.assertSetEqual(set, {"legal-statement", "to_delete"})
        self.assertEqual(key, "legal-statement + to_delete")

    def test_get_list_val_list_key_from_dict(self):
        mydict = {"toto": "tata", "end": "final"}
        list_key, list_val = DataturksGraph.get_list_val_list_key_from_dict(mydict)

        self.assertListEqual(list_key, ["toto", "end"])
        self.assertListEqual(list_val, ["tata", "final"])