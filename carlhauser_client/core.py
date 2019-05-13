#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import logging.config
import argparse
import pathlib

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from carlhauser_client.API.carlhauser_client import API_caller
# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))

# ==================== ------ LAUNCHER ------- ====================
class launcher_handler():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.API = self.get_api()

    def launch(self):
        self.logger.info(f"Launching webservice ...")
        self.perform_ping_check()
        self.perform_upload()

    def get_api(self):
        # Generate the API access point link to the hardcoded server
        cert = pathlib.Path("./cert.pem").resolve()
        # See : https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        api = API_caller(url='https://localhost:5000/', certificate_path=False)  # TODO : Should be =cert
        logging.captureWarnings(True)  # TODO : Remove
        return api

    def perform_ping_check(self):
        self.API.ping_server()

    def perform_upload(self):
        self.API.add_picture_server(pathlib.Path("./image.jpg"))


if __name__ == '__main__':
    launcher = launcher_handler()
    launcher.launch()

