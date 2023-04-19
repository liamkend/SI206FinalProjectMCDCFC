import json
import matplotlib as plt
import os
import requests
import sqlite3

def get_city(db):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()
    return city

def get_date():
    date = year + '-' + day + '-' + month
    return date

def get_weather_data():
    url = 'http://api.weatherstack.com/historical'
    key = '6065327eb56f1efe78274c0de25adead'
    city = get_city()
    date = get_date()

    try:
        r = requests.get(url + '?access_key=' + key + '&query=' + city + '&historical_date=' + date + '&hourly=1&interval=1')
        return json.loads(r.text)
    except:
        print('Error: Could not get request')
        return None
    
def load_rest_data(db):
    d = {}
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()

    cur.execute(f"SELECT restaurants.name, categories.category, buildings.building, restaurants.rating FROM restaurants JOIN buildings ON restaurants.building_id = buildings.id JOIN categories ON restaurants.category_id = categories.id")
    for row in cur:
        d[row[0]] = {'category': row[1], 'building': row[2], 'rating': row[3]}
    
    cur.close()
    return d

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