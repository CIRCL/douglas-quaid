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
    def test_get_api(self):
        pass

    def test_get_custom_api(self):
        pass

    def test_utility_extract_and_log_response(self):
        pass

    def test_utility_image_to_HTTP_payload(self):
        pass
    
    def test_utility_request_id_to_HTTP_payload(self):
        pass

    def test_ping_server(self):
        pass

    def test_ping_server_GET(self):
        pass

    def test_ping_server_POST(self):
        pass    
        
    def test_add_picture_server(self):
        pass

    def test_request_picture_server(self):
        pass

    def test_retrieve_request_results(self):
        pass

    def test_poll_until_result_ready(self):
        pass
        
    def test_is_request_result_ready(self):
        pass

    def test_export_db_server(self):
        pass
        
    '''

if __name__ == '__main__':
    unittest.main()
