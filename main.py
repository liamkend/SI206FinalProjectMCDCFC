from bs4 import BeautifulSoup
import requests
import json
import unittest
import os
import re

def write_json(filename, dict):
    with open(filename, 'w') as outFile:
        json.dump(dict, outFile)

# When storing the data from pro-football-reference, format it as:
# dictionary = {'Team1 v Team2': (city, 09/05/2003, other ...), 'Team3 v Team4': (city, 04/10/2023, other ...), ...}

# need to format the dictionary to put in files
def create_game_files(gamesDict):
    for game in gamesDict:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = dir_path + '/' + game + '.json'

        city = game[0]
        month = re.search('^(\d{2})-', game[1])
        day = re.search('-(\d{2})-', game[1])
        year = re.search('-(\d{4})$', game[1])

        weather = get_weather_data(city, month, day, year)
        write_json(filename, weather)

class TestHomework6(unittest.TestCase):
    def test():
        pass
    
if __name__ == "__main__":
    unittest.main(verbosity=2)