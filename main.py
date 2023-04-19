from ESPN import create_tables
from ESPN import add_25_to_db
from weatherAPI import create_tables
from weatherAPI import insert_weather_data
import os
import sqlite3

# def write_json(filename, dict):
#     with open(filename, 'w') as outFile:
#         json.dump(dict, outFile)

# When storing the data from pro-football-reference, format it as:
# dictionary = {'Team1 v Team2': (city, 09/05/2003, other ...), 'Team3 v Team4': (city, 04/10/2023, other ...), ...}

# need to format the dictionary to put in files
# def create_game_files(gamesDict):
#     for game in gamesDict:
#         dir_path = os.path.dirname(os.path.realpath(__file__))
#         filename = dir_path + '/' + game + '.json'

#         city = game[0]
#         month = re.search('^(\d{2})-', game[1])
#         day = re.search('-(\d{2})-', game[1])
#         year = re.search('-(\d{4})$', game[1])

#         weather = get_weather_data(city, month, day, year)
#         write_json(filename, weather)

# class TestHomework6(unittest.TestCase):
#     def test():
#         pass
    
# if __name__ == "__main__":
#     unittest.main(verbosity=2)

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def calc_season_avgs(db):
    cur, conn = setUpDatabase(db)

    cur.execute('SELECT AVG(total_pts_scored), AVG(total_yrds_gained), AVG(total_turnovers) FROM Games')
    for row in cur:
        avg_pts = round(row[0], 1)
        print('Average Points per Game: ', str(avg_pts))
        avg_yrds = round(row[1], 1)
        print('Average Yards per Game: ', str(avg_yrds))
        avg_turnovers = round(row[2], 1)
        print('Average Turnovers per Game: ', str(avg_turnovers))

def calc_betting_pcts(db):
    cur, conn = setUpDatabase(db)

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


