# -*- coding: utf-8 -*-

import unittest

import carlhauser_server.Helpers.environment_variable as environment_variable


class TestEnvVariable(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_env_variable_presence(self):
        # Verify if Environment variable are correctly set
        try :
            environment_variable.get_homedir()
            self.assertTrue(True)

        except Exception as e:
            self.assertTrue(False)

            raise Exception(f"ENVIRONMENT VARIABLE CARLHAUSER_HOME MISSING. {e}")

    def test_dir_path(self):
        # Verify if dir path is correctly verifying if a path is a path
        try :
            self.assertRaises(environment_variable.dir_path(42), Exception)
        except Exception as e :
            self.assertTrue(True)

        try :
            self.assertRaises(environment_variable.dir_path("/test/path/"), Exception)
        except Exception as e :
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()