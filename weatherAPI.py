import json
import matplotlib as plt
import os
import requests
import sqlite3

def create_tables(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Weather")
    cur.execute('CREATE TABLE Weather (id INTEGER PRIMARY KEY, city TEXT UNIQUE, date TEXT UNIQUE, temperature INTEGER, type TEXT UNIQUE, wind INTEGER, precipitation INTEGER, visability INTEGER)')
    conn.commit()

def add_25_to_db(cur, conn):
    url = 'http://api.weatherstack.com/historical'
    key = '6065327eb56f1efe78274c0de25adead'

    cur.execute(f"SELECT Cities.city, Dates.date FROM Games JOIN Cities ON Games.city_id = Cities.id JOIN Dates ON Games.date_id = Dates.id")
    games_list = cur.execute(f"SELECT * FROM Games")

    for game in games_list:
        city = game[3]
        date = game[4]

        try:
            city_id = cur.execute(f"SELECT id FROM Teams WHERE city = '{city}'").fetchone()[0]
            date_id = cur.execute(f"SELECT id FROM Dates WHERE date = '{date}'").fetchone()[0]
                    
            cur.execute('SELECT city_id, date_id FROM Games')

            found = 'No'
            for row in cur:
                if (city_id, date_id) == row:
                    found = 'Yes'
            if found == "Yes":
                continue
            else:
                r = requests.get(url + '?access_key=' + key + '&query=' + city + '&historical_date=' + date + '&hourly=1&interval=1')
                weather_dict = json.loads(r.text)
                weather = weather_dict['current']
        except:
            print('Error: Could not get request for ' + city + ' on ' + date)
            return None

        temp = weather['temperature']
        type = weather['weather_description']
        wind = weather['wind_speed']
        precip = weather['precip']
        vis = weather['visability']

        cur.execute('INSERT OR IGNORE INTO Weather (city, date, temperature, type, wind, precipitation, visibility) VALUES (?, ?, ?, ?, ?, ?, ?)', [city, date, temp, type, wind, precip, vis])
        conn.commit()