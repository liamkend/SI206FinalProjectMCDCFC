#PYTHON FILE FOR SCRAPING ESPN
import requests
from bs4 import BeautifulSoup
import os
import sqlite3

def create_tables(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Teams")
    cur.execute('CREATE TABLE Teams (id INTEGER PRIMARY KEY, team_name TEXT UNIQUE)')
    cur.execute("DROP TABLE IF EXISTS Dates")
    cur.execute('CREATE TABLE Dates (id INTEGER PRIMARY KEY, date TEXT UNIQUE)')
    cur.execute("DROP TABLE IF EXISTS Cities")
    cur.execute('CREATE TABLE Cities (id INTEGER PRIMARY KEY, city TEXT UNIQUE)')
    cur.execute("DROP TABLE IF EXISTS OverUnder")
    cur.execute('CREATE TABLE OverUnder (id INTEGER PRIMARY KEY, overunder TEXT UNIQUE)')
    cur.execute("DROP TABLE IF EXISTS Games")
    cur.execute('CREATE TABLE Games (id INTEGER PRIMARY KEY, home_team_id INTEGER, away_team_id INTEGER, city_id INTEGER, date_id INTEGER, total_pts_scored INTEGER, total_yrds_gained INTEGER, total_pass_yrds INTEGER, total_rush_yrds INTEGER, total_turnovers INTEGER, overunder INTEGER)')
    conn.commit()

def get_NFL_data(url, cur, conn, counter):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    days_list = soup.find_all('section', class_ = 'Card gameModules')
    for day in days_list:
        games_list = day.find_all('section', class_ = 'Scoreboard bg-clr-white flex flex-auto justify-between')
        for game in games_list:
            if counter < 25:
                callouts = game.find('div', class_ = 'Scoreboard__Callouts flex items-center mv4 flex-column')
                links = callouts.find_all('a')
                if len(links) == 1:             #this is an exception for Damar Hamlin game
                    continue
                boxscore_endlink = links[1].get('href', None)
                base_link = 'https://www.espn.com'
                boxscore_link = base_link + boxscore_endlink
                response = response = requests.get(boxscore_link)
                boxscoresoup = BeautifulSoup(response.content, 'html.parser')
                sections_list = boxscoresoup.find_all('li', class_ = 'Nav__Secondary__Menu__Item flex items-center n7 relative n7 Nav__AccessibleMenuItem_Wrapper')
                for section in sections_list:
                    if section.find('span').text == 'Team Stats':
                        teamstats_endlink = section.find('a').get('href', None)
                teamstats_link = base_link + teamstats_endlink
                response = requests.get(teamstats_link)
                statssoup = BeautifulSoup(response.content, 'html.parser')

                #GETTING TEAM NAMES
                team_names = []
                top_header = statssoup.find('div', class_ = 'Gamestrip__Competitors relative flex')
                name_areas = top_header.find_all('div', class_ = 'ScoreCell__Truncate Gamestrip__Truncate h4 clr-gray-01')
                for name_area in name_areas:
                    team_name = name_area.find('h2').text
                    team_names.append(team_name)
                away_team = team_names[0]
                home_team = team_names[1]

                #GETTING DATE
                game_info = statssoup.find('section', class_ = 'Card GameInfo')
                game_info_meta = game_info.find('div', class_ = 'n8 GameInfo__Meta')
                full_date = game_info_meta.find_all('span')[0].text
                date_split = full_date.split(" ")
                year = date_split[4]
                day = date_split[3].replace(',', '')
                if date_split[2] == 'September':
                    month = '09'
                elif date_split[2] == 'October':
                    month = '10'
                elif date_split[2] == 'November':
                    month = '11'
                elif date_split[2] == 'December':
                    month = '12'
                elif date_split[2] == 'January':
                    month = '01'
                elif date_split[2] == 'February':
                    month = '02'
                final_date = f"{year}-{day}-{month}"

                #GETTING CITY
                location_area = game_info.find('div', class_ = 'Weather')
                location = location_area.find('span').text
                if ',' in location:
                    split_location = location.split(",")
                    final_location = split_location[0]
                else:
                    final_location = location

                #GETTING TOTAL POINTS
                score_areas = top_header.find_all('div', class_ = 'Gamestrip__ScoreContainer flex flex-column items-center justify-center relative')
                total_score = 0
                for score_area in score_areas:
                    score = int(score_area.find('div', class_ = 'Gamestrip__Score relative tc w-100 fw-heavy h2 clr-gray-01').text)
                    total_score += score

                #GETTING TOTAL YARDS
                main_stats = statssoup.find('section', class_ = 'Card TeamStatsTable')
                table = main_stats.find('tbody', class_ = 'Table__TBODY')
                rows = table.find_all('tr')
                total_yrds_row = rows[7]
                columns = total_yrds_row.find_all('td')
                total_yards = 0
                for i in range(1, len(columns)):
                    team_yards = int(columns[i].text)
                    total_yards += team_yards

                #GETTING PASS YARDS
                total_pass_yards_row = rows[10]
                columns = total_pass_yards_row.find_all('td')
                total_pass_yards = 0
                for i in range(1, len(columns)):
                    team_pass_yards = int(columns[i].text)
                    total_pass_yards += team_pass_yards

                #GETTING RUSHING YARDS
                total_rush_yards_row = rows[15]
                columns = total_rush_yards_row.find_all('td')
                total_rush_yards = 0
                for i in range(1, len(columns)):
                    team_rush_yards = int(columns[i].text)
                    total_rush_yards += team_rush_yards

                #GETTING TOTAL TURNOVERS
                total_turnovers_row = rows[20]
                columns = total_turnovers_row.find_all('td')
                total_turnovers = 0
                for i in range(1, len(columns)):
                    team_turnovers = int(columns[i].text)
                    total_turnovers += team_turnovers

                #GETTING OVER/UNDER
                betting_area = game_info.find('div', class_ = 'betting-details-with-logo')
                ou_line = betting_area.find('div', class_ = 'n8 GameInfo__BettingItem flex-expand ou').text
                ou = float(ou_line.split(" ")[1])
                if total_score > ou:
                    ou_result = 'Over'
                elif total_score < ou:
                    ou_result = 'Under'
                else:
                    ou_result = 'Push'
                

                #INSERTING DATA INTO DATABASE
                try:
                    home_team_id = cur.execute(f"SELECT id FROM Teams WHERE team_name = '{home_team}'").fetchone()[0]
                    away_team_id = cur.execute(f"SELECT id FROM Teams WHERE team_name = '{away_team}'").fetchone()[0]
                    date_id = cur.execute(f"SELECT id FROM Dates WHERE date = '{final_date}'").fetchone()[0]
                    
                    cur.execute('SELECT home_team_id, away_team_id, date_id FROM Games')
                    found = 'No'
                    for row in cur:
                        if (home_team_id, away_team_id, date_id) == row:
                            found = 'Yes'
                    if found == "Yes":
                        continue
                    else:
                        city_id = cur.execute(f"SELECT id FROM Cities WHERE city = '{final_location}'").fetchone()[0]
                        ou_id = cur.execute(f"SELECT id FROM OverUnder WHERE overunder = '{ou_result}'").fetchone()[0]
                        cur.execute('INSERT OR IGNORE INTO Games (home_team_id, away_team_id, city_id, date_id, total_pts_scored, total_yrds_gained, total_pass_yrds, total_rush_yrds, total_turnovers, overunder) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                            [home_team_id, away_team_id, city_id, date_id, total_score, total_yards, total_pass_yards, total_rush_yards, total_turnovers, ou_id])
                        conn.commit()
                        counter += 1
                except:
                
                    cur.execute('INSERT OR IGNORE INTO Teams (team_name) VALUES (?)', [away_team])
                    cur.execute('INSERT OR IGNORE INTO Teams (team_name) VALUES (?)', [home_team])
                    cur.execute('INSERT OR IGNORE INTO Dates (date) VALUES (?)', [final_date])
                    cur.execute('INSERT OR IGNORE INTO Cities (city) VALUES (?)', [final_location])
                    cur.execute('INSERT OR IGNORE INTO OverUnder (overunder) VALUES (?)', [ou_result])

                    home_team_id = cur.execute(f"SELECT id FROM Teams WHERE team_name = '{home_team}'").fetchone()[0]
                    away_team_id = cur.execute(f"SELECT id FROM Teams WHERE team_name = '{away_team}'").fetchone()[0]
                    date_id = cur.execute(f"SELECT id FROM Dates WHERE date = '{final_date}'").fetchone()[0]
                    city_id = cur.execute(f"SELECT id FROM Cities WHERE city = '{final_location}'").fetchone()[0]
                    ou_id = cur.execute(f"SELECT id FROM OverUnder WHERE overunder = '{ou_result}'").fetchone()[0]

                    cur.execute('INSERT OR IGNORE INTO Games (home_team_id, away_team_id, city_id, date_id, total_pts_scored, total_yrds_gained, total_pass_yrds, total_rush_yrds, total_turnovers, overunder) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                            [home_team_id, away_team_id, city_id, date_id, total_score, total_yards, total_pass_yards, total_rush_yards, total_turnovers, ou_id])
                    conn.commit()
                
                    counter += 1

    return counter

#RUN FILE AND/OR CLEAR TABLES

#add_25_to_db('206_Final_project.db')                #this line will add 25 items to db
#create_tables('206_Final_project.db')                #this line will clear all of the tables



