#PYTHON FILE FOR SCRAPING PRO FB REFERENCE
import requests
import json
from bs4 import BeautifulSoup
import re

first_pfb_ref_url = 'https://www.pro-football-reference.com/years/2022/week_1.htm'
pf_ref_data = {}

response = requests.get(first_pfb_ref_url)
soup = BeautifulSoup(response.content, 'html.parser')
#print(soup)
games_list = soup.find_all('div', class_ = 'game_summary expanded nohover')
link_start = 'https://www.pro-football-reference.com'
print(len(games_list))
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
    #print(date)
    pf_ref_data[final_teams]['Date'] = date

    #GETTING THE CITY NAME
    stadium_tag = div_list[2].find('a')
    stadium_link_end = stadium_tag.get('href', None)
    stadium_full_link = link_start + stadium_link_end
    response = requests.get(stadium_full_link)
    stadiumsoup = BeautifulSoup(response.content, 'html.parser')
    paragraph_list = stadiumsoup.find_all('p')
    full_address = paragraph_list[0].text
    print(full_address)
    if len(re.findall('')) > 0:
        city = re.findall('')[0]





#STEPS
#For each game on this page... go to the games page
#Collect all necessary info from the game's page and store in the dict
#Same for each game on this page... collect link to next page
#Go to the next page