# -*- coding: utf-8 -*-

import logging
import unittest


class TestAPIExtendedAPI(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()

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
