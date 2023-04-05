from bs4 import BeautifulSoup
import requests
import json
import unittest
import os
import re

def load_json(filename):
    try:
        with open(filename, 'r') as inFile:
            data = inFile.read()
            d = json.loads(data)
    except:
        d = {}
    return d

def write_json(filename, dict):
    with open(filename, 'w') as outFile:
        json.dump(dict, outFile)

# When storing the data from pro-football-reference, format it as:
# dictionary = {'Team1 v Team2': [city, 09/05/2003, other ...], 'Team3 v Team4': [city, 04/10/2023, other ...], ...}
def get_football_data():
    pass

def get_weather_data(city, month, day, year):
    url = 'http://api.weatherstack.com/historical'
    key = '6065327eb56f1efe78274c0de25adead'
    date = year + '-' + day + '-' + month
    try:
        r = requests.get(url + '?access_key=' + key + '&query=' + city + '&historical_date=' + date + '&hourly=1&interval=1')
        return json.loads(r.text)
    except:
        print('Error: Could not get request')
        return None

def cache_games(gamesDict):
    for game in gamesDict:
        filename = game

        city = game[0]
        month = re.search('^(\d{2})-', game[1])
        day = re.search('-(\d{2})-', game[1])
        year = re.search('-(\d{4})$', game[1])

        get_weather_data(city, month, day, year)

    d = load_json(filename)
    r = requests.get(people_url)
    page = json.loads(r.text)
    next = page.get('next')
    num = 1
    page_num = 'page 1'

    if page_num not in d:
        d[page_num] = page.get('results')
    
    while next:
        num += 1
        page_num = 'page ' + str(num)
        page = get_swapi_info(next)
        if page_num not in d:
            d[page_num] = page.get('results')
        next = page.get('next')
        
    write_json(filename, d)

class TestHomework6(unittest.TestCase):
    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.filename = dir_path + '/' + "weather_api.json"
        self.cache = load_json(self.filename)

    def test_write_json(self):
        write_json(self.filename, self.cache)
        dict1 = load_json(self.filename)
        self.assertEqual(dict1, self.cache)

    def test_get_weather(self):
        newyork = get_weather_data('New York', '01', '21', '2015')
        self.assertEqual(type(newyork), dict)
        self.assertEqual(get_weather_data('Detroit', '13', '20', '2020'), None)
        print(newyork)
    
if __name__ == "__main__":
    unittest.main(verbosity=2)