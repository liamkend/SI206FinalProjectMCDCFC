import requests
import json

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