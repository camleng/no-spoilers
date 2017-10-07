from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dateutil.parser import parse
from datetime import date, timedelta
from collections import defaultdict
from contextlib import suppress
from termcolor import colored
import json
import re


def get_chromedriver() -> webdriver:
    options = Options()
    options.add_argument('headless')
    return webdriver.Chrome(executable_path='chromedrivers/chromedriver', chrome_options=options)

def pro_event(event: str) -> bool:
    for sponsor in [['ESL', 'Pro'], ['ESL', 'One'], ['ECS'], ['PGL'], ['Dreamhack'], ['FACEIT'], ['EPICENTER', 'Americas']]:
        if all(word in event for word in sponsor):
            return True
    else:
        return False

def other_favorite(teams: list) -> bool:
    return any(team in ['GX', 'Torqued'] for team in teams)

def filter_matches(all_matches: dict) -> dict:
    filtered_matches = defaultdict(list)
    number = 0
    for date, matches in all_matches.items():
        for match in matches:
            teams = [cell.text for cell in match.find_elements_by_class_name('team-cell')]
            event = match.find_element_by_class_name('event').text
            url = match.find_element_by_class_name('a-reset').get_attribute('href')
            if pro_event(event) or other_favorite(teams):
                number += 1
                filtered_matches[date].append({'team1': teams[0], 'team2': teams[1], 'url': url, 'number': number})
    return filtered_matches

def human_readable(date: date) -> str:
    header = ''
    if date == date.today():
        header = 'Today'
    elif date == date.today() + timedelta(days=-1):
        header = 'Yesterday'
    else:
        header = date.strftime('%B %-d')
    return f'{header}:'

def get_matchlist_by_day() -> list:
    return driver.find_element_by_class_name('results-all').find_elements_by_class_name('results-sublist')

def get_all_matches(matchlist_by_day: list) -> dict:
    all_matches = defaultdict(list)
    for sublist in matchlist_by_day:
        text = sublist.find_element_by_class_name('standard-headline').text[12:]
        date = parse(text).date()
        all_matches[date] = sublist.find_elements_by_class_name('result-con')
    return all_matches

def list_matches(matches: list) -> None:
    for date, matchList in matches.items():
        print(human_readable(date))
        for match in matchList:
            print(f"    {match['number']}) {color(match['team1'])} - {color(match['team2'])}")
        print()

def choose_match() -> int:
    while True:
        with suppress(ValueError):
            return int(input('Choose match: '))

def find_vods(number: int, matches: dict) -> list:
    for _, matchlist in matches.items():
        for match in matchlist:
            if match['number'] == number:
                driver.get(match['url'])
                return [vod for vod in driver.find_elements_by_class_name('stream-box') if english_vod(vod)]

def list_vods(english_vods: list) -> None:
    if not english_vods:
        print('No English VODs available')

    print('\nVODs:')
    for vod in english_vods:
        print(f"    {vod.text.split()[0]} -> {vod.get_attribute('data-stream-embed')}")

def english_vod(vod) -> bool:
    try:
        return vod.find_element_by_tag_name('img').get_attribute('alt') in ['United Kingdom', 'United States', 'USA']
    except Exception:
        return False

def color(text: str) -> str:
    return colored(text, colors[text], attrs=['bold']) if text in colors else text

if __name__ == '__main__':
    with open('team_colors.json') as f:
        colors = json.loads(f.read())

    url = 'https://www.hltv.org/results'
    driver = get_chromedriver()
    driver.get(url)

    matchlist_by_day = get_matchlist_by_day()
    all_matches = get_all_matches(matchlist_by_day)
    filtered_matches = filter_matches(all_matches)

    english_vods = []
    while not english_vods:
        list_matches(filtered_matches)

        match_number = choose_match()
        english_vods = find_vods(match_number, filtered_matches)
    list_vods(english_vods)

    driver.quit()
