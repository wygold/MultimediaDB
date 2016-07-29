import urllib.parse
import urllib.request
import pprint
import json




def get_movie_details(movie_title, movie_year):
    query = {
        'i' : '',
        't' : movie_title,
        'y' : movie_year
    }

    API_URL = "http://www.omdbapi.com/?"
    query_url = API_URL + urllib.parse.urlencode(query)
    response = urllib.request.urlopen(query_url)

    str_response = response.readall().decode('utf-8')
    json_data = json.loads(str_response)

    # dump response data in a readable format
    return json_data

def get_movie_details_title(movie_title):
    query = {
        'i' : '',
        't' : movie_title
    }

    API_URL = "http://www.omdbapi.com/?"
    query_url = API_URL + urllib.parse.urlencode(query)
    response = urllib.request.urlopen(query_url)

    str_response = response.readall().decode('utf-8')
    json_data = json.loads(str_response)

    # dump response data in a readable format
    return json_data