from ESPN import create_tables as ctESPN
from weatherAPI import create_tables as ctWAPI
from ESPN import add_25_to_db as add25ESPN
from weatherAPI import add_25_to_db as add25WAPI
import os
import sqlite3

def setUpDatabase(db):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db)
    cur = conn.cursor()
    return cur, conn

def emptyDatabase(cur, conn):
    ctESPN(cur, conn)
    ctWAPI(cur, conn)

def insertIntoDatabase(cur, conn):
    week_info = [('1','2'), ('2','2'), ('3','2'), ('4','2'), ('5','2'), ('6','2'), ('7','2'), 
                 ('8','2'), ('9','2'), ('10','2'), ('11','2'), ('12','2'), ('13','2'), ('14','2'), 
                 ('15','2'), ('16','2'), ('17','2'), ('18','2'), ('1','3'), ('2','3'), 
                 ('3','3'), ('5','3')]
    counter = 0
    for week in week_info:
        week_url = f"https://www.espn.com/nfl/scoreboard/_/week/{week[0]}/year/2022/seasontype/{week[1]}"
        counter = add25ESPN(week_url, cur, conn, counter)
        add25WAPI(cur, conn)
    return counter

def calc_season_avgs(db, cur, conn):
    cur.execute('SELECT AVG(total_pts_scored), AVG(total_yrds_gained), AVG(total_turnovers) FROM Games')
    for row in cur:
        avg_pts = round(row[0], 1)
        print('Average Points per Game: ', str(avg_pts))
        avg_yrds = round(row[1], 1)
        print('Average Yards per Game: ', str(avg_yrds))
        avg_turnovers = round(row[2], 1)
        print('Average Turnovers per Game: ', str(avg_turnovers))

def calc_betting_pcts(db, cur, conn):
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


cur, conn = setUpDatabase('206_Final_Project.db')

emptyDatabase(cur, conn)
#for i in range(13):
insertIntoDatabase(cur, conn)
#calc_betting_pcts(db, cur, conn)