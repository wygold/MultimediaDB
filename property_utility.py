__author__ = 'ywang'

import configparser
import os
import logging
from logging import handlers
from collections import OrderedDict

class property_utility:

    logger = ''

    def initialize_log(self, log_level = None, log_file =None ):
        logger = logging.getLogger(__name__)

        if log_level is None:
            logger.setLevel(logging.INFO)
        else :
            logger.setLevel(log_level)

        if logger.handlers == []:
            # create a file handler
            handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            if log_level is None:
                handler.setLevel(logging.INFO)
            else:
                handler.setLevel(log_level)

            # add the handlers to the logger
            logger.addHandler(handler)

    def set_log_level(self, log_level):
        logger = logging.getLogger(__name__)
        for handler in logger.handlers:
            if log_level is not None:
                handler.setLevel(log_level)
            else:
                handler.setLevel(log_level)

    def parse_property_file(self,property_file_dictory=None, property_file=None):
        parameters=OrderedDict()
        general_parameters = OrderedDict()
        movie_parameters = OrderedDict()
        tv_parameters = OrderedDict()
        photo_parameters = OrderedDict()
        log_parameters = OrderedDict()


        #read in property file
        config = configparser.RawConfigParser()
        if property_file_dictory is None or property_file is None :
            property_file_dictory = os.getcwd()
            property_file = 'property.txt'
            config.read(property_file_dictory + '\\'+ property_file)
        else :
            config.read(property_file_dictory + '\\'+ property_file)

        #read in log
        log_parameters['log_level'] = config.get('log', 'log_level')
        log_parameters['log_directory'] = config.get('log', 'log_directory')

        #define paramaters
        parameters['general'] = general_parameters
        parameters['movie'] = movie_parameters
        parameters['tv'] = tv_parameters
        parameters['photo'] = photo_parameters
        parameters['log'] = log_parameters

        #read in preperties
        #read in general
        general_parameters['download_folders'] = config.get('general', 'download_folders')

        #read in movie
        movie_parameters['movie_folder'] = config.get('movie', 'movie_folder')
        movie_parameters['movie_file'] = config.get('movie', 'movie_file')

        #read in tv
        tv_parameters['tv_folder'] = config.get('tv', 'tv_folder')

        return parameters

    def __init__(self, log_level=logging.INFO, log_file=None):
        pass

    def run(self):
        parameters = self.parse_property_file()

        for keys,contents in parameters.items():

            for subkey, subcontent in contents.items():
                print(subkey,"=", subcontent)
                print (parameters[keys][subkey])
        return parameters

if __name__ == "__main__":
    prop_util = property_utility()
    prop_util.run()