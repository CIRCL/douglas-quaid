# -*- coding: utf-8 -*-
import logging
import subprocess
import pathlib
import pprint

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.core as core
from carlhauser_server.Helpers.environment_variable import get_homedir
from carlhauser_server.Helpers.json_import_export import Custom_JSON_Encoder

class Test_database_conf(database_conf.Default_database_conf):
    def __init__(self):
        super().__init__()

        # ============================== SCRIPTS ==============================
        self.DB_SCRIPTS_PATH = pathlib.Path('carlhauser_server', 'Data', 'database_scripts')
        # Cache, storage and test scripts directories
        self.DB_SCRIPTS_PATH_CACHE = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')
        self.DB_SCRIPTS_PATH_STORAGE = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')
        self.DB_SCRIPTS_PATH_TEST = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')

        # ============================== SOCKETS ==============================
        self.DB_SOCKETS_PATH = pathlib.Path('carlhauser_server', 'Data', 'database_sockets')
        # Cache, storage and test scripts directories
        self.DB_SOCKETS_PATH_CACHE = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')
        self.DB_SOCKETS_PATH_STORAGE = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')
        self.DB_SOCKETS_PATH_TEST = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')

class TestDatabaseHandler():

    def __init__(self):
        self.logger = logging.getLogger()

        self.db_handler = None
        self.worker_handler = None

        self.db_conf = None
        self.dist_conf = None
        self.fe_conf = None
        self.ws_conf = None

        self.core_launcher = None

    def setUp(self, db_conf: database_conf.Default_database_conf = None,
              dist_conf: distance_engine_conf.Default_distance_engine_conf = None,
              fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None,
              ws_conf: webservice_conf.Default_webservice_conf = None):
        # Set up the database

        # Create a configuration files if none is provided
        self.db_conf = database_conf.Default_database_conf() if db_conf is None else db_conf
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf() if dist_conf is None else dist_conf
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf() if fe_conf is None else fe_conf
        self.ws_conf = webservice_conf.Default_webservice_conf() if ws_conf is None else ws_conf

        # Log config files
        json_encoder = Custom_JSON_Encoder()
        self.logger.debug(f"Configuration db_conf : {pprint.pformat(json_encoder.encode(self.db_conf))}")
        self.logger.debug(f"Configuration dist_conf : {pprint.pformat(json_encoder.encode(self.dist_conf))}")
        self.logger.debug(f"Configuration fe_conf : {pprint.pformat(json_encoder.encode(self.fe_conf))}")
        self.logger.debug(f"Configuration ws_conf : {pprint.pformat(json_encoder.encode(self.ws_conf))}")

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(db_conf=self.db_conf)

        # Overwrite configuration of db handler
        self.overwrite_socket_and_script_db_handler(self.db_handler, self.db_conf)

        # Launch test Redis DB
        if not self.db_handler.socket_test.is_running():
            self.db_handler.socket_test.launch()
            # subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=(self.db_handler.launch_test_script_path.parent))

        # Time for the socket to be opened
        self.db_handler.socket_test.wait_until_running()

        # Create launcher handler to perform other launching operation
        self.core_launcher = core.launcher_handler()

        # Overwrite configuration
        self.core_launcher.db_conf = self.db_conf
        self.core_launcher.dist_conf = self.dist_conf
        self.core_launcher.fe_conf = self.fe_conf
        self.core_launcher.ws_conf = self.ws_conf
        self.core_launcher.db_handler = self.db_handler

        self.core_launcher.start_adder_workers()
        self.core_launcher.start_requester_workers()
        self.core_launcher.start_feature_workers()
        self.core_launcher.start_webservice()
        self.core_launcher.check_worker()

    def overwrite_socket_and_script_db_handler(self, db_handler: database_start_stop.Database_StartStop, db_conf: database_conf.Default_database_conf):
        # Replace all attributes of db_handler by test database values

        # Specific attributes
        db_handler.cache_socket_path = get_homedir() / db_conf.DB_SOCKETS_PATH / 'test.sock'
        db_handler.storage_socket_path = get_homedir() / db_conf.DB_SOCKETS_PATH / 'test.sock'

        # Cache scripts
        db_handler.launch_cache_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "run.sh"
        db_handler.shutdown_cache_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "shutdown.sh"
        db_handler.flush_cache_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "shutdown.sh"

        # Storage scripts
        db_handler.launch_storage_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "run.sh"
        db_handler.shutdown_storage_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "shutdown.sh"
        db_handler.flush_storage_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "shutdown.sh"

        # Setting test-database scripts, sockets, ... paths
        db_handler.test_socket_path = get_homedir() / db_conf.DB_SOCKETS_PATH / 'test.sock'
        db_handler.launch_test_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "run.sh"
        db_handler.shutdown_test_script_path = get_homedir() / db_conf.DB_SCRIPTS_PATH / "shutdown.sh"

    def tearDown(self):
        # Shut down the database

        self.core_launcher.stop()

        # Launch shutdown AND FLUSH script
        if self.db_handler.socket_test.is_running():
            self.db_handler.socket_test.shutdown()
            # subprocess.Popen([str(self.db_handler.shutdown_test_script_path)],cwd=self.db_handler.test_socket_path.parent)

        # If start and stop are too fast, then it can't stop nor start, as it can't connect
        # e.g. because the new socket couldn't be create as the last one is still here

        self.db_handler.socket_test.wait_until_stopped()
        self.logger.info(f"Redis test database successfully stopped (ping verified)")
