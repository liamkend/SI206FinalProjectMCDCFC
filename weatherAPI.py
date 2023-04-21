import json
import requests

def create_tables(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Weather")
    cur.execute('CREATE TABLE Weather (id INTEGER PRIMARY KEY, city_id INTEGER, date_id INTEGER, type_id INTEGER, temperature INTEGER, wind INTEGER, precipitation INTEGER, visibility INTEGER)')
    cur.execute("DROP TABLE IF EXISTS Type")
    cur.execute('CREATE TABLE Type (id INTEGER PRIMARY KEY, type TEXT UNIQUE)')
    conn.commit()

def get_weather_data(cur, conn):
    url = 'http://api.weatherstack.com/historical'
    key = '6065327eb56f1efe78274c0de25adead'
    games = cur.execute("SELECT * FROM Games")

    for game in list(games):
        city_id = game[3]
        date_id = game[4]

        city = cur.execute(f"SELECT city FROM Cities WHERE id = '{city_id}'").fetchone()[0]
        date = cur.execute(f"SELECT date FROM Dates WHERE id = '{date_id}'").fetchone()[0]
        cur.execute('SELECT city_id, date_id FROM Weather')
        try:
            found = 'No'
            for row in cur:
                if (city_id, date_id) == row:
                    found = 'Yes'
            if found == "Yes":
                continue
            else:
                try:
                    r = requests.get(url + '?access_key=' + key + '&query=' + city + '&historical_date=' + date + '&hourly=1&interval=1')
                    weather_dict = json.loads(r.text)
                    weather = weather_dict['current']
                except:
                    print('Error: Could not get request for ' + city + ' on ' + date)
                    return None

                temp = weather['temperature']
                type = weather['weather_descriptions'][0]
                wind = weather['wind_speed']
                precip = weather['precip']
                vis = weather['visibility']

                type_id = cur.execute(f"SELECT id FROM Type WHERE type = '{type}'").fetchone()[0]
                cur.execute('INSERT OR IGNORE INTO Weather (city_id, date_id, type_id, temperature, wind, precipitation, visibility) VALUES (?, ?, ?, ?, ?, ?, ?)', [city_id, date_id, type_id, temp, wind, precip, vis])
                conn.commit()
        except:
            cur.execute('INSERT OR IGNORE INTO Type (type) VALUES (?)', [type])
            type_id = cur.execute(f"SELECT id FROM Type WHERE type = '{type}'").fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO Weather (city_id, date_id, type_id, temperature, wind, precipitation, visibility) VALUES (?, ?, ?, ?, ?, ?, ?)', [city_id, date_id, type_id, temp, wind, precip, vis])
            conn.commit()