#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import logging.config
import argparse
import pathlib
import subprocess
import datetime
# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Configuration.database_conf as database_conf

from carlhauser_server.API.carlhauser_server import FlaskAppWrapper
import carlhauser_server.Configuration.webservice_conf as webservice_conf

import carlhauser_server.DatabaseAccessor.database_adder as database_adder
import carlhauser_server.Helpers.json_import_export as json_import_export

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_server", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))

# ==================== ------ LAUNCHER ------- ====================
class launcher_handler():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Worker lists
        self.adder_worker_list = []

    def launch(self):
        # Create configuration
        db_conf = database_conf.Default_database_conf()
        ws_conf = webservice_conf.Default_webservice_conf()

        # Launch elements
        self.start_database(db_conf)
        self.start_adder_workers(db_conf)
        self.start_webservice(ws_conf, db_conf)

    def start_database(self, db_conf):
        self.logger.info(f"Launching redis database (x2) ...")

        # Create database handler from configuration file
        db_handler = database_start_stop.Database_StartStop(conf=db_conf)

        # Launch redis db (cache and storage)
        db_handler.launch_all_redis()

    def start_adder_workers(self, db_conf):
        self.logger.info(f"Launching to_add worker (x{db_conf.ADDER_WORKER_NB}) ...")

        # Save current configuration
        tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
        json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)

        for _ in range(db_conf.ADDER_WORKER_NB) :
            # Create the worker and start him
            init_date = datetime.date.today()

            # Open the worker subprocess with the configuration argument
            worker_path = get_homedir() / pathlib.Path('carlhauser_server','DatabaseAccessor','database_worker.py')
            proc_worker = subprocess.Popen([str(worker_path), '-c', str(tmp_db_conf_path.resolve())])

            # Store the reference to the worker
            self.adder_worker_list.append([proc_worker,init_date])


            # proc_worker = database_adder.Database_Adder(db_conf)
            # proc_worker.start()


    def start_webservice(self, ws_conf, db_conf):
        self.logger.info(f"Launching webservice ...")

        # Create configuration file
        ws_conf.CERT_FILE = pathlib.Path(ws_conf.CERT_FILE).resolve()
        ws_conf.KEY_FILE = pathlib.Path(ws_conf.KEY_FILE).resolve()

        # Create Flask endpoint from configuration files
        api = FlaskAppWrapper('api', conf=ws_conf, db_conf=db_conf)
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
