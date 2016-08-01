#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
PyGetSubtitle: download subtitles according to a video file with right click
Copyright (C) 2014 SeganW(http://fclef.wordpress.com/about)
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#from __future__ import unicode_literals
from os.path import getsize, splitext, basename
from hashlib import md5 as hashlib_md5
import guessit
import json
from json import loads as json_loads
from sys import argv, getfilesystemencoding

#Python3 support
try:
    from urllib.request import Request, urlopen, urlretrieve
    from urllib.parse import urlencode
    from urllib.error import HTTPError
except ImportError:
   # from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode, urlretrieve

SHOOTER_URL = 'http://shooter.cn/api/subapi.php'
SUBDB_URL = lambda hash: "http://api.thesubdb.com/?action=download&hash={}&language=en".format(hash)
PGS_UA = {'User-Agent': "SubDB/1.0 (PyGetSubTitle/0.1; http://github.com/truebit/PyGetSubtitle)"}
ASSRT_URL = "http://api.assrt.net/v1/sub/search?"
ASSRT_DETAIL_URL ="http://api.assrt.net/v1/sub/detail?"
ASSRT_TOKEN = "jR4VQSwspLhs50lAQRNyeOaygpPzfiQz"


def md5_hash(file_path):
    """this hash function receives the name of the file and returns the hash code"""
    readsize = 64 * 1024
    with open(file_path, 'rb') as f:
        data = f.read(readsize)
        f.seek(-readsize, 2)
        data += f.read(readsize)
    return hashlib_md5(data).hexdigest()



def request(url, data, headers=PGS_UA):
    """not using requests library due to rule of no-3rd-party-lib"""
    if data and isinstance(data, dict):
        data = dict([k.encode('utf-8'), v.encode('utf-8')] for k, v in data.items())
        data = urlencode(data).encode()
    req = Request(url, data=data, headers=headers)
    resp = urlopen(req).read()
    return resp

def subdb_downloader(file_path):
    """see http://thesubdb.com/api/"""
    hash = md5_hash(file_path)
    try:
        resp = request(SUBDB_URL(hash), None)
    except HTTPError as he:
        if he.code == 404:
            print ('no subtitle found on thesubdb.com')
        elif he.code == 400:
            print ('invalid request to thesubdb.com')
        return False
    f_name, file_extension = splitext(file_path)
    with open('{}.srt'.format(f_name), "wb") as subtitle:
        subtitle.write(resp)
    return True

def assrt_downloader(file_path):
    #get file name
    f_name, file_extension = splitext(file_path)

    #search for the subtitle with file name, it will return subtitle id
    resp = request(ASSRT_URL, data={'q': f_name, 'token':ASSRT_TOKEN})
    response = resp.decode()
    print(response)

    #choose the right subtitle to download
    subs=json.loads(response)['sub']['subs']
    for sub in subs:
        if 'lang' not in sub:
            continue

        languages=sub['lang']['langlist']
        if 'langchs' in languages or 'langdou' in languages:
            resp = request(ASSRT_DETAIL_URL, data={'id': str(sub['id']), 'token': ASSRT_TOKEN})
            response = resp.decode()

            #print(response)
            try:
                download_url = json.loads(response)['sub']['subs'][0]['filelist'][0]['url']
                download_filename = json.loads(response)['sub']['subs'][0]['filelist'][0]['f']
                #print(download_url)
                #print(download_filename)
            except KeyError:
                download_url = json.loads(response)['sub']['subs'][0]['url']
                download_filename = json.loads(response)['sub']['subs'][0]['filename']
                #print(download_url)
                #print(download_filename)

            subtitle_name, subtitle_extension = splitext(download_filename)

            # Download the file from `url` and save it locally under `file_name`:
            req = Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req) as response, open(f_name+subtitle_extension, 'wb') as out_file:
                data = response.read()  # a `bytes` object
                out_file.write(data)

            return True
    return False

def main(path):
    #path = path.decode(getfilesystemencoding())
    status = assrt_downloader(path)
    if status:
        return
    else:
        subdb_downloader(path)


if __name__ == "__main__":
    main('The Girl With The Dragon Tattoo [2009].mkv')