#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os, pathlib
import argparse
# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


def get_homedir() -> pathlib.Path:
    if not os.environ.get('CARLHAUSER_HOME'):
        guessed_home = pathlib.Path(__file__).resolve().parent.parent.parent
        raise Exception(f"CARLHAUSER_HOME is missing. Run the following command (assuming you run the code from the cloned repository):\nexport CARLHAUSER_HOME='{guessed_home}'")
    return pathlib.Path(os.environ['CARLHAUSER_HOME'])

def dir_path(path):
    if pathlib.Path(path).exists():
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")