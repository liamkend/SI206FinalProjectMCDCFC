from bs4 import BeautifulSoup
import requests
import json
import unittest
import os

def get_weather(city, date):
    baseURL = 'http://api.weatherstack.com/'
    key = '6065327eb56f1efe78274c0de25adead'
    try:
        r = requests.get(baseURL + 'current?access_key=' + key + '&query=' + city + '&historical_date=' + date)
        return json.loads(r.text)
    except:
        print('Error: Could not get request')
        return None

class TestHomework6(unittest.TestCase):
    def test_get_weather(self):
        weather = get_weather('New York', '2015-21-01')
        print(weather)
    
if __name__ == "__main__":
    unittest.main(verbosity=2)