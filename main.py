from ESPN import create_tables
from ESPN import add_25_to_db
from weatherAPI import create_tables
from weatherAPI import insert_weather_data
import os
import sqlite3

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

setUpDatabase('206_Final_Project.db')