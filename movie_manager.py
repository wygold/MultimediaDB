__author__ = 'ywang'

#monitoring movies under multimedia folder
#1. update movie library file
#2. find suitable subtitle

#monitoring download movie folder
#1. move downloaded movie to correct folder

import logging
import os, os.path
import guessit
import requests
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib import request

from property_utility import property_utility
import Omdb
import getSubtitle

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
        movie_file.write('path;filename;title;year;mimetype;imdbRating\n')

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
                    try:
                        movie['year'] = file_analyze['year']
                        # get imdb rating, result also contains many other informations
                        result = Omdb.get_movie_details(movie['title'], movie['year'])


                    except KeyError:
                        result = Omdb.get_movie_details_title(movie['title'])
                        movie['year']=result['Year']

                    try:
                        movie['imdbRating'] = result['imdbRating']
                    except KeyError:
                        movie['imdbRating'] = 0

                    #output to movie file
                    movie_file.write(movie['path'] + ';' + movie['filename'] + ';' + movie['title'] + ';' + str(
                        movie['year']) + ';' + movie['mimetype'] + ';'+movie['imdbRating']+ '\n')

        movie_file.close()

    def update_movie_db(self):
        movie_folder = parameters['movie']['movie_folder']
        movies_names = []

        movie_file = open(movie_folder + '\\' + parameters['movie']['movie_file'], 'r')
        old_movie_contents = movie_file.readlines()
        for line in old_movie_contents:
            fields = line.split(';')
            movies_names.append(fields[1])
        movie_file.close()

        movie_file = open(movie_folder + '\\' + parameters['movie']['movie_file'], 'a')

        for root, _, files in os.walk(movie_folder):
            for f in files:
                if f not in movies_names:
                    movie = dict()
                    file_analyze = guessit.guessit(f)
                    # print (file_analyze)
                    if 'video' in file_analyze['mimetype'] and file_analyze['type'] == 'movie':
                        movie['path'] = root
                        movie['filename'] = f
                        movie['title'] = file_analyze['title']
                        movie['mimetype'] = file_analyze['mimetype']
                        try:
                            movie['year'] = file_analyze['year']
                            # get imdb rating, result also contains many other informations
                            result = Omdb.get_movie_details(movie['title'], movie['year'])


                        except KeyError:
                            result = Omdb.get_movie_details_title(movie['title'])
                            movie['year'] = result['Year']

                        try:
                            movie['imdbRating'] = result['imdbRating']
                        except KeyError:
                            movie['imdbRating'] = 0

                        # output to movie file
                        movie_file.write(movie['path'] + ';' + movie['filename'] + ';' + movie['title'] + ';' + str(
                            movie['year']) + ';' + movie['mimetype'] + ';' + movie['imdbRating'] + '\n')



    def retrieve_movie_subtitle(self, movie):
        # download best subtitles
        getSubtitle.main(movie)

    # move downloaded movie to correct folder
    def move_movie_to_library(self):
        movie_folder = parameters['movie']['movie_folder']
        download_folders = parameters['general']['download_folders'].split(',')

        for download_folder in download_folders:
            for root, _, files in os.walk(download_folder):
                for f in files:
                    file_ext = f.split(".")[-1]
                    file_name = f[:len(f)-len(file_ext)-1]

                    file_analyze = guessit.guessit(f)

                    try:
                        if 'video' in file_analyze['mimetype'] and file_analyze['type'] == 'movie' and not os.path.isfile(root+'//'+file_name+'.aria2'):
                            movie_year = str(file_analyze['year'])
                            if not os.path.exists(movie_folder+'//'+movie_year):
                                os.mkdir(movie_folder+'//'+movie_year)
                            os.rename(root+'//'+f, movie_folder+'//'+movie_year+'//'+f)

                            self.retrieve_movie_subtitle(root+'//'+f)


                    except KeyError:
                        continue


    def test(self,movie):
        search_url = "http://api.assrt.net/v1/sub/search?"

        params = {
            "q": movie,
            "token": 'jR4VQSwspLhs50lAQRNyeOaygpPzfiQz'
        }

        request = Request(search_url, urlencode(params).encode())
        response = urlopen(request).read().decode()
        print(response)
        id = json.loads(response)['sub']['subs'][0]['id']


        detail_url = "http://api.assrt.net/v1/sub/detail?"

        params = {
            "id": id ,
            "token": 'jR4VQSwspLhs50lAQRNyeOaygpPzfiQz'
        }

        request = Request(detail_url, urlencode(params).encode())
        response = urlopen(request).read().decode()

        try:
            download_url = json.loads(response)['sub']['subs'][0]['filelist'][0]['url']
            download_filename= json.loads(response)['sub']['subs'][0]['filelist'][0]['f']
            print(download_url)
            print(download_filename)
        except KeyError:
            download_url = json.loads(response)['sub']['subs'][0]['url']
            download_filename = json.loads(response)['sub']['subs'][0]['filename']
            print(download_url)
            print(download_filename)

        # Download the file from `url` and save it locally under `file_name`:
        req=Request(download_url,headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response, open(download_filename, 'wb') as out_file:
            data = response.read()  # a `bytes` object
            out_file.write(data)

if __name__ == "__main__":
    app = movie_manage()
    #app.create_movie_db()
    #app.update_movie_db()
    #app.move_movie_to_library()
    #app.retrieve_movie_subtitle()
    app.test('The.Big.Bang.Theory.S05E18')