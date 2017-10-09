from datetime import date, timedelta
from collections import defaultdict
from contextlib import suppress
import json

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from dateutil.parser import parse
from termcolor import colored


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


def human_readable(date: date) -> str:
    if date == date.today():
        header = 'Today'
    elif date == date.today() + timedelta(days=-1):
        header = 'Yesterday'
    else:
        header = date.strftime('%B %-d')
    return f'{header}:'


def filter_matches(sublist) -> dict:
    global match_num
    matches_for_day = get_matches_for_day(sublist)
    filtered_matches = []
    for match in matches_for_day:
        teams = get_teams(match)
        event = get_event(match)
        if pro_event(event) or other_favorite(teams):
            url = get_url(match)
            match_num += 1
            filtered_matches.append(new_match(teams, event, url))
    return filtered_matches


def get_matches_for_day(sublist) -> list:
    return find_elements('.result-con', _from=sublist)


def get_url(match) -> str:
    return find_element('.a-reset', _from=match).get_attribute('href')


def get_event(match) -> str:
    return find_element('.event', _from=match).text


def get_teams(match) -> str:
    return [cell.text for cell in find_elements('.team-cell', _from=match)]


def new_match(teams: list, event: str, url: str) -> dict:
    return {'team1': teams[0], 'team2': teams[1], 'url': url, 'number': match_num}


def get_matches() -> dict:
    matches = defaultdict(list)
    for sublist in find_elements('.results-sublist'):
        date = get_date(sublist)
        matches[date] = filter_matches(sublist)
    return matches


def get_date(sublist) -> date:
    text = find_element('.standard-headline', _from=sublist).text[12:]
    return parse(text).date()

def list_matches(matches: dict) -> None:
    for date, matchlist in matches.items():
        print(human_readable(date))
        for match in matchlist:
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
                return get_vods()

def get_vods() -> list:
    english_countries = ['United States', 'United Kingdom', 'Canada']
    vods = get_vod_elements()
    if not vods:
        return None
    english_vods = [vod for vod in vods if vod.get_attribute('alt') in english_countries]
    if english_vods:
        return english_vods
    else:
        print('\nNo English VODs available')
        return vods


def get_vod_elements():
    try:
        return find_elements('.stream-box[data-stream-embed]')
    except Exception:
        print('No VODs available')


def list_vods(vods: list) -> None:
    if not vods:
        print('No VODs available')
        return
    
    plural = len(vods) > 1

    print(f"\nHere {('are some' if plural else 'is a')} non-English VOD{('s' if plural else '')}:")
    for vod in vods:
        stream_name = vod.text.split()[0]
        country = find_element('img[alt]', _from=vod).get_attribute('alt')
        url = vod.get_attribute('data-stream-embed')
        print(f"    {stream_name} [{country}] -> {url}")


def color(text: str) -> str:
    return colored(text, colors[text], attrs=['bold']) if text in colors else text


def find(css_selector: str, _list=True, _from=None):
    d = _from or driver
    elements = WebDriverWait(d, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
    return elements if _list else elements[0]


def find_elements(css_selector: str, _from=None) -> list:
    return find(css_selector, _list=True, _from=_from)


def find_element(css_selector: str, _from=None):
    return find(css_selector, _list=False, _from=_from)


def prompt_to_pick_another():
    while True:
        text = input('\n[Enter] to pick another or [q] to quit\n')
        if text == '':
            return True
        elif text.lower() == 'q':
            return False


if __name__ == '__main__':
    with open('team_colors.json') as f:
        colors = json.loads(f.read())

    driver = get_chromedriver()
    url = 'https://www.hltv.org/results'
    driver.get(url)

    match_num = 0
    matches = get_matches()

    picking_another = True
    while picking_another:
        list_matches(matches)
        selected_match = choose_match()
        vods = find_vods(selected_match, matches)
        if vods:
            list_vods(vods)
        picking_another = prompt_to_pick_another()

    driver.quit()
