from ESPN import create_tables as ctESPN
from weatherAPI import create_tables as ctWAPI
from ESPN import get_NFL_data as insertESPN
from weatherAPI import get_weather_data as insertWAPI
import matplotlib.pyplot as plt
import os
import json
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
        counter = insertESPN(week_url, cur, conn, counter)
        insertWAPI(cur, conn)

def write_json(filename, dict):
    with open(filename, 'w') as outFile:
        json.dump(dict, outFile, indent=2)

def calc_season_avgs(cur):
    d = {}
    cur.execute('SELECT AVG(total_pts_scored), AVG(total_yrds_gained), AVG(total_turnovers) FROM Games')
    for row in cur:
        avg_pts = round(row[0], 1)
        d['Points per Game'] = avg_pts
        avg_yrds = round(row[1], 1)
        d['Yards per Game'] = avg_yrds
        avg_turnovers = round(row[2], 1)
        d['Turnovers per Game'] = avg_turnovers
    return d

def calc_betting_pcts(cur):
    ou_dict = {}
    d = {}
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
        d[type[0]] =  f"{pct}%"
    return d

def clear_plot():
    plt.clf()

def create_pass_yrds_scatters(cur):
    pass_yrds_list = []
    wind_list = []
    visibility_list = []
    cur.execute('SELECT Games.total_pass_yrds, Weather.wind, Weather.visibility FROM Games JOIN Weather ON Games.city_id = Weather.city_id AND Games.date_id = Weather.date_id')
    for row in list(cur):
        pass_yrds_list.append(row[0])
        wind_list.append(row[1])
        visibility_list.append(row[2])
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax1.scatter(pass_yrds_list, wind_list)
    ax1.set_title("Total Passing Yards by Wind Speeds")
    ax1.set_xlabel("Passing Yards")
    ax1.set_ylabel("Wind Speed (mph)")
    ax1.set_xlim(0,1000)
    ax2 = fig.add_subplot(122)
    ax2.scatter(pass_yrds_list, visibility_list)
    ax2.set_title("Total Passing Yards by Visibility")
    ax2.set_xlabel("Passing Yards")
    ax2.set_ylabel("Visibility")
    ax2.set_xlim(0,1000)
    plt.show()

def create_pts_by_temp_plot(cur):
    total_pts_list = []
    temp_list = []
    cur.execute('SELECT Games.total_pts_scored, Weather.temperature FROM Games JOIN Weather ON Games.city_id = Weather.city_id AND Games.date_id = Weather.date_id')
    for row in list(cur):
        total_pts_list.append(row[0])
        temp_list.append(row[1])
    plt.scatter(temp_list, total_pts_list)
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Total Points Scored')
    plt.title('Total Points Scored by Outdoor Temperature')
    plt.show()

def create_turnover_by_weather_plot(cur):
    turnovers_by_weather = {}
    cur.execute('SELECT Games.total_turnovers, Weather.type_id FROM Games JOIN Weather ON Games.city_id = Weather.city_id AND Games.date_id = Weather.date_id')
    for row in list(cur):
        turnovers = row[0]
        type_id = row[1]
        weather_type = cur.execute(f"SELECT type FROM Type WHERE id = '{type_id}'").fetchone()[0]
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
    plt.xlabel('Weather Types')
    plt.ylabel('Average Turnovers per Game')
    plt.title('Average Turnovers per Game by Weather Type')
    plt.show()

def create_pct_rush_yrds_by_weather_plot(cur):
    pcts = {}
    cur.execute('SELECT Games.total_rush_yrds, Games.total_yrds_gained, Weather.type_id FROM Games JOIN Weather ON Games.city_id = Weather.city_id AND Games.date_id = Weather.date_id')
    for row in list(cur):
        rush_yrds = row[0]
        total_yrds = row[1]
        pct_rush_yrds = round((rush_yrds / total_yrds), 1)
        type_id = row[2]
        weather_type = cur.execute(f"SELECT type FROM Type WHERE id = '{type_id}'").fetchone()[0]
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
    plt.xlabel('Weather Types')
    plt.ylabel('Rushing Yards Pcertange per Game')
    plt.title('Rushing Yards Percentage per Game by Weather Type')
    plt.show()

def create_ou_pie_charts_by_weather(cur):
    ou_dict = {}
    fig = plt.figure()
    cur.execute('SELECT Games.overunder, OverUnder.overunder, Weather.type_id FROM Games JOIN Weather ON Games.city_id = Weather.city_id AND Games.date_id = Weather.date_id JOIN OverUnder ON Games.overunder = OverUnder.id')
    for row in list(cur):
        ou_id = row[0]
        ou = row[1]
        type_id = row[2]
        weather_type = cur.execute(f"SELECT type FROM Type WHERE id = '{type_id}'").fetchone()[0]
        if weather_type not in ou_dict:
            ou_dict[weather_type] = {}
        if ou not in ou_dict[weather_type].keys():
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
        if push_total == None:
            push_total = 0
        pie_ready = [over_total, under_total, push_total]
        total = sum(pie_ready)
        labels_list = ['Over', 'Under', 'Push']
        # ??
        ax = fig.add_subplot(int(f"12{counter}"))
        ax.pie(pie_ready, labels = labels_list, autopct=lambda p: '{:.0f}%'.format(p * total / 100))
        ax.set_title(f"Over/Under: {weather_type}")
    plt.show()


cur, conn = setUpDatabase('206_Final_Project.db')
emptyDatabase(cur, conn)
#insertIntoDatabase(cur, conn)
for i in range(12):
    insertIntoDatabase(cur, conn)

d = {}
dir_path = os.path.dirname(os.path.realpath(__file__))
d['Season Averages'] = calc_season_avgs(cur)
d['Betting Percentages'] = calc_betting_pcts(cur)
write_json(dir_path + '/' + "calculated_data.json", d)

create_pass_yrds_scatters(cur)
clear_plot()
create_pts_by_temp_plot(cur)
clear_plot()
create_turnover_by_weather_plot(cur)
clear_plot()
create_pct_rush_yrds_by_weather_plot(cur)
clear_plot()
#create_ou_pie_charts_by_weather(cur)
clear_plot()