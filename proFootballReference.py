#PYTHON FILE FOR SCRAPING PRO FB REFERENCE
import requests
import json
from bs4 import BeautifulSoup
import re

first_pfb_ref_url = 'https://www.pro-football-reference.com/years/2022/week_1.htm'
pf_ref_data = {}

#def add_nfl_week_to_dict(week_url, final_dict)
response = requests.get(first_pfb_ref_url)
soup = BeautifulSoup(response.content, 'html.parser')
#print(soup)
games_list = soup.find_all('div', class_ = 'game_summary expanded nohover')
link_start = 'https://www.pro-football-reference.com'
#print(len(games_list))
for game in games_list:
    link_section = game.find('td', class_ = 'right gamelink')
    link_tag = link_section.find('a')
    link_end = link_tag.get('href', None)
    full_link = link_start + link_end
    response = requests.get(full_link)
    gamesoup = BeautifulSoup(response.content, 'html.parser')

    #GETTING THE TEAMS
    scorebox = gamesoup.find('div', class_ = 'scorebox')
    strongs_list = scorebox.find_all('strong')
    
    names_list = []
    for strong in strongs_list:
        if len(strong.find_all('a')) > 0:
            team_name = strong.find('a').text
            names_list.append(team_name)
    final_teams = names_list[0] + ' vs ' + names_list[1]
    #print(final_teams)
    pf_ref_data[final_teams] = {}
    
    #GETTING THE DATE
    scorebox_meta = scorebox.find('div', class_ = 'scorebox_meta')
    div_list = scorebox_meta.find_all('div')
    date = div_list[0].text
    date_split = date.split(' ')
    year = date_split[3]
    day = date_split[2].replace(',', '')
    if date_split[1] == 'Aug':
        month = '08'
    elif date_split[1] == 'Sep':
        month = '09'
    elif date_split[1] == 'Oct':
        month = '10'
    elif date_split[1] == 'Nov':
        month = '11'
    elif date_split[1] == 'Dec':
        month = '12'
    elif date_split[1] == 'Jan':
        month = '01'
    elif date_split[1] == 'Feb':
        month = '02'
    # else:
    #     month = '00'
    final_date = f"{year}-{day}-{month}"
    pf_ref_data[final_teams]['Date'] = final_date

    #GETTING THE CITY NAME
    stadium = div_list[2].find('a').text
    #print(stadium)
    if stadium == 'Tottenham Stadium':
        stadium = 'Tottenham Hotspur Stadium'
    response = requests.get('https://en.wikipedia.org/wiki/List_of_current_National_Football_League_stadiums')
    stadiumsoup = BeautifulSoup(response.content, 'html.parser')
    stadium_table = stadiumsoup.find('table', style = 'font-size:90%;')
    #print(len(stadium_table))
    body = stadium_table.find('tbody')
    rows = body.find_all('tr')
    for i in range(1, len(rows)):
        columns = rows[i].find_all('td')
        wikiname = rows[i].find('th').find('a').text
        if stadium == wikiname:
            city = columns[2].find('a').text
            final_city = city.split(',')[0]
            #print(final_city)
            pf_ref_data[final_teams]['City'] = final_city
    
    others_table = stadiumsoup.find('table', style = 'font-size:90%')
    others_body = others_table.find('tbody')
    others_rows = others_body.find_all('tr')
    for i in range(1, len(others_rows)):
        o_columns = others_rows[i].find_all('td')
        o_wikiname = others_rows[i].find('th').find('a').text
        if stadium == o_wikiname:
            city = o_columns[2].find('a').text
            final_city = city.split(',')[0]
            #print(final_city)
            pf_ref_data[final_teams]['City'] = final_city
    
    #GETTING ROOF TYPE
    #print(gamesoup)
    #game_info = gamesoup.find('div', id = "div_game_info")
    #print(game_info)
    #roof_section = game_info.find('tbody')
    #print(roof_section)

print(pf_ref_data)





#STEPS
#For each game on this page... go to the games page
#Collect all necessary info from the game's page and store in the dict
#Same for each game on this page... collect link to next page
#Go to the next page