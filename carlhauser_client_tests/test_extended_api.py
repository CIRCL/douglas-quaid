# -*- coding: utf-8 -*-

import logging
import pathlib
import unittest
from pprint import pformat

from carlhauser_client.API.extended_api import Extended_API, update_values_dict
from common.environment_variable import get_homedir


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_client_tests/test_Helpers/id_generator")
        self.extended_api = Extended_API.get_api()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    ''' 
    # TODO !
    def test_get_api(self):
        pass

    def test_add_pictures_to_db(self):
        pass

    def test_request_similar_and_wait(self):
        pass

    def test_request_pictures(self):
        pass
        
    def test_get_db_dump_as_graph(self):
        pass

    '''

if __name__ == '__main__':
    unittest.main()
