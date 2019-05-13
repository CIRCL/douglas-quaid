#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import logging.config
import argparse
import pathlib

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Helpers.environment_variable import get_homedir
from carlhauser_server.API.carlhauser_server import FlaskAppWrapper
import carlhauser_server.Configuration.webservice_conf as webservice_conf
# from . import helpers
# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_server", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))

# ==================== ------ LAUNCHER ------- ====================
class launcher_handler():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def launch(self):
        self.logger.info(f"Launching webservice ...")
        self.start_webservice()

    def start_webservice(self):
        # Create configuration file
        ws_conf = webservice_conf.Default_webservice_conf()
        ws_conf.CERT_FILE = pathlib.Path(ws_conf.CERT_FILE).resolve()
        ws_conf.KEY_FILE = pathlib.Path(ws_conf.KEY_FILE).resolve()

        # Create Flask endpoint
        api = FlaskAppWrapper('api', conf=ws_conf)
        api.add_all_endpoints()

        # Run Flask API endpoint
        api.run() # debug=True

if __name__ == '__main__':
    launcher = launcher_handler()
    launcher.launch()



'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage backend DBs.')
    parser.add_argument("--start", action='store_true', default=False, help="Start all")
    parser.add_argument("--stop", action='store_true', default=False, help="Stop all")
    parser.add_argument("--status", action='store_true', default=True, help="Show status")
    args = parser.parse_args()

    if args.start:
        launch_all()
    if args.stop:
        stop_all()
    if not args.stop and args.status:
        check_all()
'''
