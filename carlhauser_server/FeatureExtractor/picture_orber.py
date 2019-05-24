#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys

import cv2
import numpy as np

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf


class Picture_Orber():
    def __init__(self, fe_conf: feature_extractor_conf):
        # STD attributes
        self.fe_conf = fe_conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Picture Hasher")
        self.algo = cv2.ORB_create(nfeatures=fe_conf.ORB_KEYPOINTS_NB)

    def orb_picture(self, curr_picture):
        answer = {}
        self.logger.info("Orbing picture ... ")

        # orb_pic =  np.array(curr_picture)
        arr = np.asarray(bytearray(curr_picture), dtype=np.uint8)
        orb_pic = cv2.imdecode(arr, -1)
        self.logger.debug(f"Picture converted to CV2 UMAT {type(orb_pic)}")

        # DEBUG # cv2.imwrite('/home/user/Desktop/debug_orb.bmp', orb_pic)

        try:
            # Note : @image must be a PIL instance.
            if self.fe_conf.ORB:
                # Picture loading handled in picture load_image overwrite
                key_points, descriptors = self.algo.detectAndCompute(orb_pic, None)

                # Store representation information in the picture itself
                answer["ORB_KEYPOINTS"] = key_points
                answer["ORB_DESCRIPTORS"] = descriptors

                if key_points is None:
                    self.logger.warning(f"WARNING : picture has no keypoints")
                if descriptors is None:
                    self.logger.warning(f"WARNING : picture has no descriptors")

        except Exception as e:
            self.logger.error("Error during orbing : " + str(e))

        return answer

    '''
        def check_null_hash(self, hash):
        # Check if the hash provided is null/None/empty. If yes, provide a default hash

        if not hash or hash is None or hash == "":
            return '0000000000000000000000000000000000000000000000000000000000000000000000'
        return hash
    
    '''