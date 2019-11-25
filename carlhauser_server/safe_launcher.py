#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import pathlib
import signal
import sys
import time
import traceback

from contextlib import contextmanager

from common.environment_variable import get_homedir

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_server", "logging.ini")).resolve()

@contextmanager
def replaced_signal(s, f):
    original_handler = signal.getsignal(s)
    signal.signal(s, f)
    try:
        yield
    except:
        raise   # reraise exceptions
    finally:
        signal.signal(s, original_handler)

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

    def launch(self, auto_stop=False, use_input=True):
        with replaced_signal(signal.SIGTERM, self.exit_gracefully):
            try:
                self._do_launch()

                time.sleep(1)

                if auto_stop:
                    self._do_stop()
                elif use_input:
                    should_stop = False

                    while not should_stop:
                        print("Press any key to stop ... ")

                        input()
                        print("Are you sure you want to stop ? [yes/no] ")
                        value = input()
                        if value == "yes":
                            should_stop = True

                    self._do_stop()
                else:
                    signal.pause()

            except KeyboardInterrupt:
                self.logger.info('Handling keyboard interrupt')
                try:
                    self._do_stop()
                    # TODO : Handle interrupt and shutdown, and clean ...
                    sys.exit(0)
                except SystemExit:
                    traceback.print_exc(file=sys.stdout)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                self.logger.error(f'An error occured during execution: {e}')
                self._do_stop()
                sys.exit(2)

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
        :param signum: ? Automatic
        :param frame:  ? Automatic
        :return: ? Automatic
        """

        try:
            self.logger.info("Stopping all processes gracefully")
            self._do_stop()
            sys.exit(0)

        except KeyboardInterrupt:
            self.logger.warning("Forcing termination, you should be nicer to carl-hauser")
            sys.exit(1)
