#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import io
import logging
import tlsh

import PIL.Image as Image
import imagehash

import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class Picture_Hasher:
    def __init__(self, fe_conf: feature_extractor_conf):
        # STD attributes
        self.fe_conf = fe_conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Picture Hasher")

    def hash_picture(self, curr_picture):
        """
        Hash a picture and returns the hash value
        :param curr_picture: the picture to hash
        :return: the hashed version of the picture
        """
        answer = {}
        self.logger.info("Hashing picture ... ")

        # Convert bytes in PIL image
        pil_picture = Image.open(io.BytesIO(curr_picture))
        self.logger.debug(f"Picture converted to PIL Image {type(pil_picture)}")

        # DEBUG # pil_picture.save('/home/user/Desktop/debug_pil.bmp')

        try:
            # Note : @image must be a PIL instance.
            if self.fe_conf.A_HASH.get("is_enabled", False):
                self.logger.debug("A-HASH ... ")
                answer["A_HASH"] = self.check_null_hash(imagehash.average_hash(pil_picture))
            if self.fe_conf.P_HASH.get("is_enabled", False):
                self.logger.debug("P_HASH ... ")
                answer["P_HASH"] = self.check_null_hash(imagehash.phash(pil_picture))
            if self.fe_conf.P_HASH_SIMPLE.get("is_enabled", False):
                self.logger.debug("P_HASH_SIMPLE ... ")
                answer["P_HASH_SIMPLE"] = self.check_null_hash(imagehash.phash_simple(pil_picture))
            if self.fe_conf.D_HASH.get("is_enabled", False):
                self.logger.debug("D_HASH ... ")
                answer["D_HASH"] = self.check_null_hash(imagehash.dhash(pil_picture))
            if self.fe_conf.D_HASH_VERTICAL.get("is_enabled", False):
                self.logger.debug("D_HASH_VERTICAL ... ")
                answer["D_HASH_VERTICAL"] = self.check_null_hash(imagehash.dhash_vertical(pil_picture))
            if self.fe_conf.W_HASH.get("is_enabled", False):
                self.logger.debug("W_HASH ... ")
                answer["W_HASH"] = self.check_null_hash(imagehash.whash(pil_picture))
            if self.fe_conf.TLSH.get("is_enabled", False):
                self.logger.debug("TLSH ... ")
                answer["TLSH"] = self.check_null_hash(tlsh.hash(curr_picture))

        except Exception as e:
            self.logger.error("Error during hashing : " + str(e))

        return answer

    def check_null_hash(self, tmp_hash):
        """
        Check if the provided hash is none, if so, provide a "null version" of the hash.
        :param tmp_hash: the hash to check
        :return: a "null" version of the hash if "None", the hash itself without modification otherwise.
        """
        # Check if the hash provided is null/None/empty. If yes, provide a default hash
        self.logger.debug("Checking hash ... ")

        if not tmp_hash:
            return '0000000000000000000000000000000000000000000000000000000000000000000000'
        return tmp_hash
