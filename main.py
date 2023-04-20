from ESPN import create_tables
from ESPN import add_25_to_db
from weatherAPI import create_tables
from weatherAPI import insert_weather_data
import os
import sqlite3
import matplotlib as plt

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

def create_pass_yrds_scatters(db):
    cur, conn = setUpDatabase(db)
    pass_yrds_list = []
    wind_list = []
    visibility_list = []
    cur.execute('SELECT Games.total_pass_yrds, Weather.wind, Weather.vis FROM Games JOIN Weather ON Games.city_id = Weahter.city_id AND Games.date_id = Weather.date_id')
    for row in cur:
        pass_yrds_list.append(row[0])
        wind_list.append(row[1])
        visibility_list.append(row[2])
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax1.scatter(pass_yrds_list, wind_list)
    ax1.set_title("Total Passing Yards by Wind Speeds")
    ax1.set_xlim(0,1000)
    ax2 = fig.add_subplot(122)
    ax2.scatter(pass_yrds_list, visibility_list)
    ax2.set_title("Total Passing Yards by Visibility")
    ax2.set_xlim(0,1000)

    plt.show()

def create_pts_by_temp_plot(db):
    cur, conn = setUpDatabase(db)
    total_pts_list = []
    temp_list = []
    cur.execute('SELECT Games.total_pts_scored, Weather.temp FROM Games JOIN Weather ON Games.city_id = Weahter.city_id AND Games.date_id = Weather.date_id')
    for row in cur:
        total_pts_list.append(row[0])
        temp_list.append(row[1])
    plt.scatter(temp_list, total_pts_list)
    plt.set_xlabel('Temperature')
    plt.set_ylabel('Total Points Scored')
    plt.set_title('Total Points Scored by Outdoor Temperature')
    plt.show()

def create_turnover_by_weather_plot(db):
    cur, conn = setUpDatabase(db)
    turnovers_by_weather = {}
    cur.execute('SELECT Games.total_turnovers, Weather.type FROM Games JOIN Weather ON Games.city_id = Weahter.city_id AND Games.date_id = Weather.date_id')
    for row in cur:
        turnovers = row[0]
        weather_type = row[1]
        if weather_type not in turnovers_by_weather.keys():
            turnovers_by_weather[weather_type] = [turnovers]
        else:
            turnovers_by_weather[weather_type].append(turnovers)
    for type in turnovers_by_weather.items():
        count = 0
        total_turnovers = 0
        for value in type[1]:
            count += 1
            total_turnovers += value
        avg_turnovers = round((total_turnovers / count), 1)
        turnovers_by_weather[type[0]] = avg_turnovers
    weather_types_list = turnovers_by_weather.keys()
    avg_turnovers_list = turnovers_by_weather.values()

    plt.bar(weather_types_list, avg_turnovers_list)
    plt.set_xlabel('Weather Types')
    plt.set_ylabel('Average Turnovers per Game')
    plt.set_title('Average Turnovers per Game by Weather Type')
    plt.show()

def create_pct_rush_yrds_by_weather_plot(db):
    cur, conn = setUpDatabase(db)
    pcts = {}
    cur.execute('SELECT Games.total_rush_yrds, Games.total_yrds_gained, Weather.type FROM Games JOIN Weather ON Games.city_id = Weahter.city_id AND Games.date_id = Weather.date_id')
    for row in cur:
        rush_yrds = row[0]
        total_yrds = row[1]
        pct_rush_yrds = round((rush_yrds / total_yrds), 1)
        weather_type = row[2]
        if weather_type not in pcts.keys():
            pcts[weather_type] = [pct_rush_yrds]
        else:
            pcts[weather_type].append(pct_rush_yrds)
    for type in pcts.items():
        count = 0
        total_pct = 0
        for value in type[1]:
            count += 1
            total_pct += value
        avg_pct_rush_yrds = round((total_pct / count), 1)
        pcts[type[0]] = avg_pct_rush_yrds
    weather_types_list = pcts.keys()
    avg_pct_rush_yrds_list = pcts.values()

    plt.bar(weather_types_list, avg_pct_rush_yrds_list)
    plt.set_xlabel('Weather Types')
    plt.set_ylabel('Pcertange of Rushing Yards per Game')
    plt.set_title('Percentage of Rushing Yards per Game by Weather Type')
    plt.show()

def create_ou_pie_charts_by_weather(db):
    cur, conn = setUpDatabase(db)

    ou_dict = {}
    fig = plt.figure()
    cur.execute('SELECT Games.overunder, OverUnder.overunder, Weather.type FROM Games JOIN Weather ON Games.id = Weather.game_id JOIN OverUnder ON Games.overunder = OverUnder.id')
    for row in cur:
        ou_id = row[0]
        ou = row[1]
        weather_type = row[2]
        if weather_type not in ou_dict:
            ou_dict[weather_type] = {}
        if ou in ou_dict[weather_type].keys():
            ou_dict[weather_type][ou] = 1
        else:
            ou_dict[weather_type][ou] += 1
    counter = 0
    for type in ou_dict.items():
        counter += 1
        weather_type = type[0]
        over_total = type[1].get('Over')
        under_total = type[1].get('Under')
        push_total = type[1].get('Push')
        pie_ready = [over_total, under_total, push_total]
        total = sum(pie_ready)
        labels_list = ['Over', 'Under', 'Push']
        ax = fig.add_suplot(int(f"12{counter}"))
        ax.pie(pie_ready, labels = labels_list, autopct=lambda p: '{:.0f}%'.format(p * total / 100))
        ax.set_title(f"Over/Under: {weather_type}")
    plt.show()
    






# calc_season_avgs('206_Final_Project.db')
# calc_betting_pcts('206_Final_Project.db')
# create_pass_yrds_scatters('206_Final_Project.db')
# create_pts_by_temp_plot('206_Final_Project.db')
# create_turnover_by_weather_plot('206_Final_Project.db')
# create_pct_rush_yrds_by_weather_plot('206_Final_Project.db')
# create_ou_pie_charts_by_weather('206_Final_Project.db')





