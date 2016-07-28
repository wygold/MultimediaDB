__author__ = 'ywang'

#monitoring movies under multimedia folder
#1. update movie library file
#2. find suitable subtitle

#monitoring download movie folder
#1. move downloaded movie to correct folder

import logging
import os, os.path
import guessit

from property_utility import property_utility


class movie_manage():

    video_extensions = ['wmv','asf','mov','avi','mp4','m4v','3gp', '3g2', 'k3g','mpeg', 'mpg', 'mpe']

    def initialize_log(self,log_level='INFO', log_file=None):
        global logger
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        if logger.handlers == []:
            # create a file handler
            handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            handler.setLevel(log_level)

            # add the handlers to the logger
            logger.addHandler(handler)

    def set_log_level(self,log_level):
        logger = logging.getLogger(__name__)
        for handler in logger.handlers:
            if log_level is not None:
                handler.setLevel(log_level)
            else:
                handler.setLevel(log_level)


    def __init__(self):
        global parameters
        property_util = property_utility()
        parameters = property_util.parse_property_file()

        #intialize logging
        log_level = parameters['log']['log_level']
        log_file = parameters['log']['log_directory'] + '\\movie_manager.log'
        self.initialize_log(log_level, log_file)

        logger.info('Movie manager starts.')

    def create_movie_db(self):
        movie_folder =  parameters['movie']['movie_folder']

        movie_file = open(movie_folder+'\\'+parameters['movie']['movie_file'], 'w')

        for root, _, files in os.walk(movie_folder):
            for f in files:
                movie = dict()
                file_analyze = guessit.guessit(f)
                #print (file_analyze)
                if 'video' in file_analyze['mimetype'] and file_analyze['type']=='movie' :
                    movie['path']=root
                    movie['filename'] = f
                    movie['title'] = file_analyze['title']
                    movie['mimetype'] = file_analyze['mimetype']
                    movie_file.write(movie['path']+'|'+movie['filename']+'|'+movie['title']+'|'+movie['mimetype'])

        movie_file.close()

    def update_movie_db(self):
        None

    def find_movie_subtitle(self):
        None

    def move_movie_to_library(self):
        None

if __name__ == "__main__":
    app = movie_manage()
    app.create_movie_db()
