#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import json, requests

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

# ==================== ------ SERVER Flask API CALLER ------- ====================
class API_caller():
    def __init__(self, url):
        self.server_url = url

    def ping_server(self):
        r = requests.get(url=self.server_url)
        print("GET request => ", r.status_code, r.reason, r.text)

        r = requests.post(url=self.server_url)
        print("POST request => ", r.status_code, r.reason, r.text)

    def send_data(self):
        create_row_data = {'id': '1235', 'name': 'Joel', 'created_on': '27/01/2018', 'modified_on': '27/01/2018', 'desc': 'This is Joel!!'}
        r = requests.post(url=self.server_url, json=create_row_data)
        print(r.status_code, r.reason, r.text)


if __name__ == '__main__':
    api = API_caller(url='http://localhost:5000/', )
    api.ping_server()
