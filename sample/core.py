# -*- coding: utf-8 -*-
# from . import helpers

# STD imports
import logging.config

# load the logging configuration
logging.config.fileConfig('logging.ini')

class main_class():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def launch(self):
        self.logger.info("==== ----- LAUNCHING MAIN CLASS ---- ==== ")


if __name__ == '__main__':
    main_class = main_class()
    main_class.launch()


'''
def get_hmm():
    """Get a thought."""
    return 'hmmm...'

def hmm():
    """Contemplation..."""
    if helpers.get_answer():
        print(get_hmm())
        
'''
