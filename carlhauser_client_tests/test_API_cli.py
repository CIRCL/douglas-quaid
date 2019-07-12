# -*- coding: utf-8 -*-

import logging
import unittest


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    ''' 
    # TODO !
    def test_ping(self):
        pass

    def test_upload(self):
        pass

    def test_request(self):
        pass

    def test_dump(self):
        pass
    '''

if __name__ == '__main__':
    unittest.main()
