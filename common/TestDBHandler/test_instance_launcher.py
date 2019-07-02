# -*- coding: utf-8 -*-
import logging
import pathlib
import pprint

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.core as core
from common.environment_variable import get_homedir
from common.ImportExport.json_import_export import Custom_JSON_Encoder


class TestInstance_database_conf(database_conf.Default_database_conf):
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


class TestInstanceLauncher:
    """ Create a running instance of douglas-quaid, all linked on a unique test database
        Modify the behavior of the core launcher handler, to use only one database. """

    def __init__(self):
        self.logger = logging.getLogger()

        # TMP and modified version of handlers that will overwrite core-launcher's ones.
        self.db_handler = None
        self.worker_handler = None

        # Configurations files
        self.db_conf = None
        self.dist_conf = None
        self.fe_conf = None
        self.ws_conf = None

        self.core_launcher = None

    # ============================== LAUNCHER ACTIONS ==============================
    def create_full_instance(self, db_conf: database_conf.Default_database_conf = None,
                             dist_conf: distance_engine_conf.Default_distance_engine_conf = None,
                             fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None,
                             ws_conf: webservice_conf.Default_webservice_conf = None):

        self.set_configurations(db_conf, dist_conf, fe_conf, ws_conf)
        self.create_modified_db_handler()
        self.create_core_launcher()
        self.launcher_core_launcher()

    def create_database_only_instance(self, db_conf: database_conf.Default_database_conf = None,
                                      dist_conf: distance_engine_conf.Default_distance_engine_conf = None,
                                      fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None,
                                      ws_conf: webservice_conf.Default_webservice_conf = None):

        self.set_configurations(db_conf, dist_conf, fe_conf, ws_conf)
        self.create_modified_db_handler()

    def tearDown(self):
        # Shut down the database
        self.core_launcher.stop()

    # ============================== PRECISE ACTIONS ==============================

    def set_configurations(self, db_conf: database_conf.Default_database_conf = None,
                           dist_conf: distance_engine_conf.Default_distance_engine_conf = None,
                           fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None,
                           ws_conf: webservice_conf.Default_webservice_conf = None):
        # Set the configuration to use.
        self.logger.debug(f"Settings configuration file on the test instance launcher")

        # Create a configuration files if none is provided
        self.db_conf = database_conf.Default_database_conf() if db_conf is None else db_conf
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf() if dist_conf is None else dist_conf
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf() if fe_conf is None else fe_conf
        self.ws_conf = webservice_conf.Default_webservice_conf() if ws_conf is None else ws_conf

        # Log config files
        json_encoder = Custom_JSON_Encoder()
        self.logger.debug(f"Registered configuration files are ... ")
        self.logger.debug(f"Configuration db_conf : \n{pprint.pformat(json_encoder.encode(self.db_conf))}")
        self.logger.debug(f"Configuration dist_conf : \n{pprint.pformat(json_encoder.encode(self.dist_conf))}")
        self.logger.debug(f"Configuration fe_conf : \n{pprint.pformat(json_encoder.encode(self.fe_conf))}")
        self.logger.debug(f"Configuration ws_conf : \n{pprint.pformat(json_encoder.encode(self.ws_conf))}")

    def create_modified_db_handler(self) -> database_start_stop.Database_StartStop:
        """ Create a database handler (start/stop), modify its configuration and launch the DB """

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(db_conf=self.db_conf, handle_test_db=True)

        # Overwrite configuration of db handler
        self.db_handler = self.overwrite_socket_and_script_db_handler(self.db_handler, self.db_conf)

        self.db_handler.launch_all_redis()
        self.db_handler.wait_until_all_redis_running()

        '''
                    # Launch test Redis DB (test, that's all)
            if not self.db_handler.socket_test.is_running():
                self.db_handler.socket_test.launch()

                # Time for the socket to be opened
                self.db_handler.socket_test.wait_until_running()
        '''

        return self.db_handler

    @staticmethod
    def overwrite_socket_and_script_db_handler(db_handler: database_start_stop.Database_StartStop, db_conf: database_conf.Default_database_conf):
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

        return db_handler

    def create_core_launcher(self):
        """ Create a core launcher and overwrite its configuraiton """

        # Create launcher handler to perform other launching operation
        self.core_launcher = core.launcher_handler()

        # Overwrite configuration
        self.core_launcher.db_conf = self.db_conf
        self.core_launcher.dist_conf = self.dist_conf
        self.core_launcher.fe_conf = self.fe_conf
        self.core_launcher.ws_conf = self.ws_conf
        self.core_launcher.db_handler = self.db_handler

        return self.core_launcher

    def launcher_core_launcher(self):
        """ Launch the whole "ecosystem" of workers around the database. Handled by the core """

        self.core_launcher.start_adder_workers()
        self.core_launcher.start_requester_workers()
        self.core_launcher.start_feature_workers()
        self.core_launcher.start_webservice()
        self.core_launcher.check_worker()

