#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import cv2
from typing import Dict
import numpy as np
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
from common.environment_variable import load_server_logging_conf_file
from carlhauser_server.Helpers.bow_orb_vocabulary_creator import BoWOrb_Vocabulary_Creator
load_server_logging_conf_file()


class Picture_BoW_Orber:
    def __init__(self, fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        self.fe_conf: feature_extractor_conf.Default_feature_extractor_conf = fe_conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Picture BoW Orber")

        self.algo = cv2.ORB_create(nfeatures=fe_conf.ORB_KEYPOINTS_NB)
        # TODO : Dictionnary path / Vocabulary
        self.bow_descriptor = cv2.BOWImgDescriptorExtractor(self.algo, cv2.BFMatcher(cv2.NORM_HAMMING))
        vocab = BoWOrb_Vocabulary_Creator.load_vocab_from_file(fe_conf.BOW_VOCAB_PATH)
        self.bow_descriptor.setVocabulary(vocab)

    '''
    def create_dict_from_folder(self, folder_path: pathlib.Path()):
        self.bow_trainer = cv2.BOWKMeansTrainer(self.conf.BOW_SIZE)

        for curr_image in picture_list:
            self.bow_trainer.add(np.float32(curr_image.description))

        self.vocab = self.bow_trainer.cluster().astype(picture_list[0].description.dtype)

    def compute_distance():
        if self.conf.BOW_CMP_HIST == configuration.BOW_CMP_HIST.CORREL:
            dist = 1 - cv2.compareHist(pic1.description, pic2.description, cv2.HISTCMP_CORREL)
        elif self.conf.BOW_CMP_HIST == configuration.BOW_CMP_HIST.BHATTACHARYYA:
            dist = cv2.compareHist(pic1.description, pic2.description, cv2.HISTCMP_BHATTACHARYYA)
        else:
            raise Exception('BOW WRAPPER : HISTOGRAM COMPARISON MODE INCORRECT')

    '''

    def bow_orb_picture(self, curr_picture, orb_dict: Dict):
        """
        BoW-Orb a picture and returns the BoW-orb value
        :param curr_picture: the picture to bow-orb
        :return: the BoW-orb version of the picture
        """
        answer = {}
        self.logger.info("BoW-Orbing picture ... ")

        # Convert from cv's BRG default color order to RGB
        # image = cv2.imread(str(path))
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.logger.debug(f"Original type {type(curr_picture)}")
        arr = np.asarray(bytearray(curr_picture), dtype=np.uint8)
        orb_pic = cv2.imdecode(arr, -1)
        self.logger.debug(f"Picture converted to CV2 UMAT {type(orb_pic)}")

        # Get keypoints from orb dictionnary OR compute it if not present
        key_points = orb_dict.get("ORB_KEYPOINTS", None)
        if key_points is None or key_points == []:
            self.logger.warning(f"No Keypoints in provided ORB dictionnary.")
            try:
                self.logger.info(f"Computing Orb Keypoints in BoW-orber.")

                # Compute keypoints by itself
                key_points, _ = self.algo.detectAndCompute(orb_pic, None)

                if key_points is None or key_points == []:
                    raise Exception("NO KEYPOINTS")

            except Exception as e:
                self.logger.error(f"Impossible to compute keypoints in BoW-Orber for provided picture : {e}")
                raise e

        if self.fe_conf.BOW_ORB.get("is_enabled", False):
            try:
                description = self.bow_descriptor.compute(orb_pic, key_points)
                self.logger.warning(f"TYPE descriptor : {type(description)}")
                answer["BOW_ORB_DESCRIPTOR"] = description
            except Exception as e:
                self.logger.error("Error during BoW-orbing : " + str(e))
                raise e

        return answer
