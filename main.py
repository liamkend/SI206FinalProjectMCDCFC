from bs4 import BeautifulSoup
import requests
import json
import unittest
import os

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

def get_weather(city, month, day, year):
    try:
        r = requests.get('http://api.weatherstack.com/historical?access_key=6065327eb56f1efe78274c0de25adead&query=' + city + '&historical_date=' + year + '-' + day + '-' + month + '&hourly=1&interval=1')
        return json.loads(r.text)
    except:
        print('Error: Could not get request')
        return None

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
        newyork = get_weather('New York', '01', '21', '2015')
        self.assertEqual(type(newyork), dict)
        self.assertEqual(get_weather('Detroit', '13', '20', '2020'), None)
        print(newyork)
    
if __name__ == "__main__":
    unittest.main(verbosity=2)