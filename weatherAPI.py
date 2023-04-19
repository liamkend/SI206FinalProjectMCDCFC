import json
import matplotlib as plt
import os
import requests
import sqlite3

def create_tables(db):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS Weather")
    cur.execute('CREATE TABLE Weather (id INTEGER PRIMARY KEY, city TEXT UNIQUE, date TEXT UNIQUE, temperature INTEGER, type TEXT UNIQUE, wind INTEGER, precipitation INTEGER, visability INTEGER)')
    conn.commit()

def insert_weather_data(db):
    url = 'http://api.weatherstack.com/historical'
    key = '6065327eb56f1efe78274c0de25adead'

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()
    
    cur.execute(f"SELECT Cities.city, Dates.date FROM Games JOIN Cities ON Games.city_id = Cities.id JOIN Dates ON Games.date_id = Dates.id")
    for row in cur:
        city = row[3]
        date = row[4]

        try:
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

def plot_rest_categories(db):
    d = {}
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()
    curCategory = conn.cursor()

    categories = curCategory.execute("SELECT * FROM categories")
    for row in categories:
        d[row[1]] = 0

    cur.execute("SELECT * FROM restaurants")
    for row in cur:
        category_id = row[2]

        categories = curCategory.execute("SELECT * FROM categories")
        for row in categories:
            if category_id == row[0]:
                category = row[1]
        
        d[category] += 1
    
    cur.close()
    curCategory.close()

    x = list(d.keys())
    y = list(d.values())
    plt.bar(range(len(x)), y, tick_label=x)
    plt.show()

    return d

def find_rest_in_building(building_num, db):
    l = []
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()

    cur.execute(f"SELECT buildings.building, restaurants.name, restaurants.rating FROM restaurants JOIN buildings ON restaurants.building_id = buildings.id WHERE buildings.building = {building_num} ORDER BY restaurants.rating DESC")
    for row in cur:
        l.append(row[1])

    return l