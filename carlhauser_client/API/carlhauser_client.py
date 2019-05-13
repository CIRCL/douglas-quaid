#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import json, requests
import pathlib
import ssl
import logging

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


# ==================== ------ SERVER Flask API CALLER ------- ====================
class API_caller():
    def __init__(self, url, certificate_path):
        self.server_url = url
        self.logger = logging.getLogger(__name__)
        self.cert = certificate_path

    def ping_server(self):
        r = requests.get(url=self.server_url, verify=self.cert)
        self.logger.info(f"GET request => {r.status_code} {r.reason} {r.text}")

        r = requests.post(url=self.server_url, verify=self.cert)
        self.logger.info(f"POST request => {r.status_code} {r.reason} {r.text}")

    def add_picture_server(self, file_path: pathlib.Path):
        # Solve the file path
        if not file_path.is_absolute():
            file_path = file_path.resolve()

        # Select the endpoint
        target_url = self.server_url + "add_picture"

        # Send the picture
        with open(str(file_path), 'rb') as img:
            files = {'image': (file_path.name, img, 'multipart/form-data', {'Expires': '0'})}
            with requests.Session() as s:
                r = s.put(url=target_url, files=files, verify=self.cert)
                self.logger.info(f"POST picture => {r.status_code} {r.reason} {r.text}")
                self.logger.info(r.content)

        # print(r.status_code, r.reason, r.text)
