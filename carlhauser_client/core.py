#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

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
        self.perform_upload(get_homedir() / "datasets" / "simple_pictures" / "image.jpg")
        self.logger.info(f"Add ? ")
        input()
        self.perform_upload(get_homedir() / "datasets" / "simple_pictures" / "image.png")
        self.logger.info(f"Request ? ")
        input()
        request_id = self.perform_request(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")
        self.logger.info(f"Add ? ")
        input()
        self.perform_upload(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")
        self.logger.info(f"Fetch result ? ")
        input()
        self.retrieve_request_results(request_id)
        self.logger.info(f"Dump DB ? ")
        input()
        self.export_db_server()

    def get_api(self):
        # Generate the API access point link to the hardcoded server
        cert = pathlib.Path("./cert.pem").resolve()

        # See : https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # To create : openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        api = API_caller(url='https://localhost:5000/', certificate_path=cert)  # TODO : Should be =cert
        logging.captureWarnings(True)  # TODO : Remove
        return api

    def perform_ping_check(self):
        self.API.ping_server()

    def perform_upload(self, path: pathlib.Path):
        self.API.add_picture_server(path)

    def perform_request(self, path: pathlib.Path):
        return self.API.request_picture_server(path)[1]

    def retrieve_request_results(self, path: pathlib.Path):
        return self.API.retrieve_request_results(path)[1]

    def export_db_server(self):
        return self.API.export_db_server()[1]


if __name__ == '__main__':
    launcher = launcher_handler()
    launcher.launch()
