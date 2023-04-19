from bs4 import BeautifulSoup
import requests
import json
import unittest
import os
import re
import sqlite3


def connectDatabase(db):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()
    return cur, conn

def calc_season_avgs(db):
    cur, conn = connectDatabase(db)

    cur.execute('SELECT AVG(total_pts_scored), AVG(total_yrds_gained), AVG(total_turnovers) FROM Games')
    for row in cur:
        avg_pts = round(row[0], 1)
        print('Average Points per Game: ', str(avg_pts))
        avg_yrds = round(row[1], 1)
        print('Average Yards per Game: ', str(avg_yrds))
        avg_turnovers = round(row[2], 1)
        print('Average Turnovers per Game: ', str(avg_turnovers))

def calc_betting_pcts(db):
    cur, conn = connectDatabase(db)

    ou_dict = {}
    total_games = 0
    cur.execute('SELECT id, overunder FROM OverUnder')
    for row in cur:
        ou_dict[row[0]] = [row[1]]
    for item in ou_dict.items():    
        cur.execute(f"SELECT COUNT(*) FROM Games WHERE overunder = {item[0]}")
        for row in cur:
            ou_dict[item[0]].append(row[0])
            total_games += int(row[0])

    for type in ou_dict.values():
        pct = round((int(type[1]) / total_games * 100), 2)
        print(f"{type[0]}: {pct}%")

calc_betting_pcts('206_Final_Project.db')


