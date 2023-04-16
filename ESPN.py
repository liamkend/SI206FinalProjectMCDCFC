#PYTHON FILE FOR SCRAPING ESPN
import requests
from bs4 import BeautifulSoup

def add_25_games(url, final_dict):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    days_list = soup.find_all('section', class_ = 'Card gameModules')
    for day in days_list:
        games_list = day.find_all('section', class_ = 'Scoreboard bg-clr-white flex flex-auto justify-between')
        for game in games_list:
            callouts = game.find('div', class_ = 'Scoreboard__Callouts flex items-center mv4 flex-column')
            links = callouts.find_all('a')
            boxscore_endlink = links[1].get('href', None)
            base_link = 'https://www.espn.com'
            boxscore_link = base_link + boxscore_endlink
            response = response = requests.get(boxscore_link)
            boxscoresoup = BeautifulSoup(response.content, 'html.parser')
            sections_list = boxscoresoup.find_all('li', class_ = 'Nav__Secondary__Menu__Item flex items-center n7 relative n7 Nav__AccessibleMenuItem_Wrapper')
            teamstats_endlink = sections_list[3].find('a').get('href', None)
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
            final_names = team_names[0] + ' vs ' + team_names[1]
            final_dict[final_names] = {}
            final_dict[final_names]['Away Team'] = team_names[0]
            final_dict[final_names]['Home Team'] = team_names[1]

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
            final_dict[final_names]['Date'] = final_date

            #GETTING CITY
            location_area = game_info.find('div', class_ = 'Weather')
            location = location_area.find('span').text
            if ',' in location:
                split_location = location.split(",")
                final_location = split_location[0]
            else:
                final_location = location
            final_dict[final_names]['Location'] = final_location

            #GETTING TOTAL POINTS
            score_areas = top_header.find_all('div', class_ = 'Gamestrip__ScoreContainer flex flex-column items-center justify-center relative')
            total_score = 0
            for score_area in score_areas:
                score = int(score_area.find('div', class_ = 'Gamestrip__Score relative tc w-100 fw-heavy h2 clr-gray-01').text)
                total_score += score
            final_dict[final_names]['Total Points Scored'] = total_score

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
            final_dict[final_names]['Total Yards Gained'] = total_yards

            #GETTING PASS YARDS
            total_pass_yards_row = rows[10]
            columns = total_pass_yards_row.find_all('td')
            total_pass_yards = 0
            for i in range(1, len(columns)):
                team_pass_yards = int(columns[i].text)
                total_pass_yards += team_pass_yards
            final_dict[final_names]['Total Passing Yards'] = total_pass_yards

            #GETTING RUSHING YARDS
            total_rush_yards_row = rows[15]
            columns = total_rush_yards_row.find_all('td')
            total_rush_yards = 0
            for i in range(1, len(columns)):
                team_rush_yards = int(columns[i].text)
                total_rush_yards += team_rush_yards
            final_dict[final_names]['Total Rushing Yards'] = total_rush_yards

            #GETTING TOTAL TURNOVERS
            total_turnovers_row = rows[20]
            columns = total_turnovers_row.find_all('td')
            total_turnovers = 0
            for i in range(1, len(columns)):
                team_turnovers = int(columns[i].text)
                total_turnovers += team_turnovers
            final_dict[final_names]['Total Turnovers'] = total_turnovers

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
            final_dict[final_names]['Over/Under'] = ou_result
    
    print(final_dict)


def main():
    espn_data = {}
    week_1_url = 'https://www.espn.com/nfl/scoreboard/_/week/1/year/2022/seasontype/2'
    print(add_25_games(week_1_url, espn_data))


main()

