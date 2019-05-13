# -*- coding: utf-8 -*-
from carlhauser_server_tests.context import *
from PIL import Image

import carlhauser_server.Helpers.id_generator as id_generator

import unittest

class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/id_generator")

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_exif_and_hash(self):
        self.logger.info("Verify if two pictures which are equal, but with different EXIF data, have the same hash or not \n Expected result : they do not have the same hash value")
        # TODO : Modify SHA1 function to handle same hash value of "true picture"

        file_path_1 = self.test_file_path / pathlib.Path('original.jpg')
        file_path_2 = self.test_file_path / pathlib.Path('modified.jpg')

        with open(str(file_path_1), 'rb') as img1:
            with open(str(file_path_2), 'rb') as img2:
                # Compute hashes
                hash_1 = id_generator.get_SHA1(img1)
                hash_2 = id_generator.get_SHA1(img2)

                # Print
                self.logger.debug("Original picture hash : " + hash_1)
                self.logger.debug("Modified (exif) picture hash : " + hash_2)

                # Verify if EXIF metadat change does not change the hash
                self.assertNotEqual(hash_1, hash_2)
                self.assertEqual(hash_1, "1305a22ac12deedd5cd712a7649ce37f47ae9aed")
                self.assertEqual(hash_2, "049210fca5ceb266c1a12e8afa9646e85febe121")

    '''
    Note that all files have different hashes, depending on their original format
    4eaaa80c7e1568f89b530ec7114d5bac  ./OUTPUT.jpg.bmp
    a198d87db3640032acb687c322e48077  ./OUTPUT.bmp.bmp
    c142cb5838a74aaf4e9bde5b6b26168e  ./OUTPUT.eps.bmp
    3da1cc3ff2445e010112b6ff480c9880  ./OUTPUT.gif.bmp
    f2fb0c7c4509d3a5a4bfea142d9e6558  ./OUTPUT.ico.bmp
    d9d02647dcf276885df8cb6d15c89d2c  ./OUTPUT.png.bmp
    3d7f5d36f549375535ae65121c887d11  ./OUTPUT.tga.bmp
    b4b6ced60c7ed7f575ab74e4121ee55a  ./OUTPUT.tiff.bmp
    9275b0e01add0617022c94f941a64cb3  ./OUTPUT.webp.bmp
    '''
    def test_bmp_conversion(self):
        self.logger.info("Verify if BMP conversion does work")

        file_path_1 = self.test_file_path / pathlib.Path('original.jpg')
        output_path = self.test_file_path / pathlib.Path('OUTPUT.txt')

        # TODO : Missing wbmp, svg, exr
        for i in [".jpg", ".ico", ".gif", ".png", ".tga", ".tiff", ".webp", ".bmp", ".eps"]:

            try :
                file_path_tmp = file_path_1.with_suffix(i)
                output_path_tmp = output_path.with_suffix(i + ".bmp")

                with open(str(file_path_tmp), 'rb') as img1:
                    img_bmp = id_generator.convert_to_bmp(img1)
                    # DEBUG / Write to file / id_generator.write_to_file(img_bmp, output_path_tmp)
            except :
                self.assertTrue(False)
            else :
                self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()