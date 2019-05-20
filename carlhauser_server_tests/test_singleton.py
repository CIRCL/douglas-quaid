# -*- coding: utf-8 -*-

import unittest

import carlhauser_server.Helpers.template_singleton as template_singleton


class testSingleton(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

    class Derived(metaclass=template_singleton.Singleton):
        value_shared = 0

        def __init__(self):
            super().__init__()
            self.myvalue = 0

        def get_value_shared(self):
            print("get shared value :", self.value_shared)
            return self.value_shared

        def get_myvalue(self):
            print("get personal value :", self.myvalue)
            return self.myvalue

        def increment_value(self):
            print("increment all values")

            self.value_shared += 1
            self.myvalue += 1

    def test_singleton(self):
        classe1 = self.Derived()
        classe2 = self.Derived()
        classe3 = self.Derived()

        self.assertEqual(classe1.get_value_shared(), 0)
        self.assertEqual(classe1.get_myvalue(), 0)
        classe1.increment_value()
        self.assertEqual(classe1.get_value_shared(), 1)
        self.assertEqual(classe1.get_myvalue(), 1)

        # Does it changed it on the second instance ?
        self.assertEqual(classe2.get_value_shared(), 1)
        self.assertEqual(classe2.get_myvalue(), 1)

        classe3.increment_value()
        self.assertEqual(classe3.get_value_shared(), 2)
        self.assertEqual(classe3.get_myvalue(), 2)


if __name__ == '__main__':
    unittest.main()
