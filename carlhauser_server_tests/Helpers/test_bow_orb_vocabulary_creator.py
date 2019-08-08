# -*- coding: utf-8 -*-

import logging
import unittest

import numpy as np

from carlhauser_server.Helpers.bow_orb_vocabulary_creator import BoWOrb_Vocabulary_Creator
from common.environment_variable import get_homedir


class testBowOrbVocabularCreator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        self.test_path = get_homedir() / "datasets" / "douglas-quaid-tests" / "BowOrbVocabulary"

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_save_and_load_vocab(self):
        vocab_creator = BoWOrb_Vocabulary_Creator()
        vocab = vocab_creator.create_dict_from_folder(self.test_path / "MINI_DATASET", self.test_path / "OUTPUT", 500, 500)

        vocab_creator.save_vocab_to_file(vocab, self.test_path / "OUTPUT", file_name="vocab_test.npy")
        vocab_loaded = vocab_creator.load_vocab_from_file(self.test_path / "OUTPUT" / "vocab_test.npy")

        self.logger.debug(vocab)
        self.logger.debug(vocab_loaded)
        self.assertTrue(np.array_equal(vocab, vocab_loaded))


if __name__ == '__main__':
    unittest.main()
