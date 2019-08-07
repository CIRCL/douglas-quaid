#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import pathlib
import signal
import sys
import time
import traceback

from common.environment_variable import get_homedir

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_server", "logging.ini")).resolve()


# ==================== ------ LAUNCHER ------- ====================
class SafeLauncher:
    """
    Handle a class launch with fallback method and clean exit even if brutally stopped.
    """

    def __init__(self, class_to_call=None,
                 launch_method: str = None,
                 stop_method: str = None):

        self.logger = logging.getLogger(__name__)

        self.class_to_call = class_to_call
        self.launch_method: str = launch_method
        self.stop_method: str = stop_method

    def launch(self):
        try:
            # Setting SIGINT handler
            # original_sigint = signal.getsignal(signal.SIGINT)  # Storing original
            signal.signal(signal.SIGINT, self.exit_gracefully)  # Setting custom

            self._do_launch()

            time.sleep(1)

            do_stop = False

            while not do_stop:
                print("Press any key to stop ... ")
                input()
                print("Are you sure you want to stop ? [yes/no] ")
                value = input()
                if value == "yes":
                    do_stop = True

            self._do_stop()

        except KeyboardInterrupt:
            print('Interruption detected')
            try:
                print('Handling interruptions ...')
                self._do_stop()
                # TODO : Handle interrupt and shutdown, and clean ...
                sys.exit(0)
            except SystemExit:
                traceback.print_exc(file=sys.stdout)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(f'Critical problem during execution {e}')
            self._do_stop()
            sys.exit(0)

    def _do_launch(self):
        func = getattr(self.class_to_call, self.launch_method, None)
        func()

    def stop(self):
        self._do_stop()

    def _do_stop(self):
        func = getattr(self.class_to_call, self.stop_method, None)
        func()

    def exit_gracefully(self, signum, frame):
        """
        restore the original signal handler as otherwise evil things will happen
        in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
        signal.signal(signal.SIGINT, original_sigint) # TODO : To put back ?
        :param signum: ? Automatic
        :param frame:  ? Automatic
        :return: ? Automatic
        """

        try:
            print("Wait for the extinction ... ")
            self._do_stop()
            sys.exit(1)

        except KeyboardInterrupt:
            print("You should be nicer to carl-hauser.")
            sys.exit(1)

        # restore the exit gracefully handler here
        # signal.signal(signal.SIGINT, exit_gracefully) # TODO : To put back ?
