#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib
import cv2
import numpy as np


# from carlhauser_server.Helpers import arg_parser
# from common.environment_variable import load_server_logging_conf_file

# load_server_logging_conf_file()

class BoWOrb_Vocabulary_Creator():

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def get_file_list_from_folder(folder_path: pathlib.Path):
        p = folder_path.glob('**/*')
        files = [x for x in p if x.is_file()]
        print(f"Files list : {files[:5]}... from {pathlib.Path}")
        return files

    def create_dict_from_folder(self, in_folder: pathlib.Path,
                                out_folder: pathlib.Path,
                                vocab_size: int,
                                nb_keypoints: int):
        # Extract the list of pictures to process
        files_list = self.get_file_list_from_folder(in_folder)

        # Define the nb of elements in the vocabulary we want
        # TODO : Define as a function of the number of pictures ?
        bow_trainer = cv2.BOWKMeansTrainer(vocab_size)
        algo = cv2.ORB_create(nfeatures=nb_keypoints)

        descriptors = None
        nb_corr_pictures = 0
        for curr_img_path in files_list:
            orb_pic = cv2.imread(str(curr_img_path))
            # arr = np.asarray(bytearray(orb_pic), dtype=np.uint8)
            # orb_pic = cv2.imdecode(arr, -1)
            # print(f"Picture converted to CV2 UMAT {type(orb_pic)}")

            key_points, descriptors = algo.detectAndCompute(orb_pic, None)

            if descriptors is not None :
                bow_trainer.add(np.float32(descriptors))
                nb_corr_pictures += 1
                if nb_corr_pictures % 20 == 0 :
                    print(f"Working on pictures {nb_corr_pictures} out of {len(files_list)}")
            else :
                print(f"Descriptors not usables for pictures : {curr_img_path} are {descriptors}")

        print(f"Nb Pictures processed : {nb_corr_pictures}")
        print(f"Nb Pictures discarded : {len(files_list) - nb_corr_pictures}")

        vocab = bow_trainer.cluster().astype(descriptors.dtype)
        self.save_vocab_to_file(vocab, out_folder)

        return vocab

    @staticmethod
    def save_vocab_to_file(vocab : np.ndarray, out_folder: pathlib.Path, file_name : str = "vocab.npy"):
        print(f"Saving vocabulary ...")

        print(type(vocab))
        print(vocab)

        np.save(str(out_folder / file_name), vocab)

    @staticmethod
    def load_vocab_from_file(in_file: pathlib.Path) -> np.ndarray:
        print(f"Loading vocabulary ...")
        return np.load(in_file)

def dir_path(path):
    if pathlib.Path(path).exists():
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a dictionary/vocabulary out of a folder (recursive) of pictures.')

    parser.add_argument('-s', '--source_folder', dest="source_folder", type=dir_path)
    parser.add_argument('-o', '--output_folder', dest="output_folder", type=dir_path)
    parser.add_argument('-n', '--nbwords', dest="nbwords", type=int)

    args = parser.parse_args()

    in_folder_path = pathlib.Path(args.source_folder)
    out_folder_path = pathlib.Path(args.output_folder)

    vocab_creator = BoWOrb_Vocabulary_Creator()
    vocab_creator.create_dict_from_folder(in_folder_path, out_folder_path, int(args.nbwords), 500) # 500 to 500 000
