from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dateutil.parser import parse
from datetime import date, timedelta
from collections import defaultdict


def get_chromedriver():
    options = Options()
    options.add_argument('headless')
    return webdriver.Chrome(executable_path='chromedrivers/chromedriver', chrome_options=options)

def pro_event(event: str):
    for e in ['ESL', 'PGL', 'Dreamhack', 'Faceit']:
        if e in event:
            return True
    return False

def filter_matches(all_matches: dict):
    filtered_matches = defaultdict(list)
    for date, matchlist in all_matches.items():
        for match in matchlist:
            for row in match.find_elements_by_tag_name('tr'):
                teams = [cell.text for cell in row.find_elements_by_class_name('team-cell')]
                event = row.find_element_by_class_name('event').text
                if pro_event(event) or 'GX' in teams or 'Torqued' in teams:
                    filtered_matches[date].append({'team1': teams[0], 'team2': teams[1]})
    return filtered_matches

def human(date: date):
    header = ''
    if date == date.today():
        header = 'Today'
    elif date == date.today() + timedelta(days=-1):
        header = 'Yesterday'
    else:
        header = date.strftime('%B %m')
    return f'{header}:'

def get_matches_by_days():
    return driver.find_element_by_class_name('results-all').find_elements_by_class_name('results-sublist')

if __name__ == '__main__':
    url = 'https://www.hltv.org/results'
    driver = get_chromedriver()
    driver.get(url)
    matches_by_days = get_matches_by_days()

    all_matches = defaultdict(list)
    for match in matches_by_days[:2]: # latest day
        text = match.find_element_by_class_name('standard-headline').text[12:]
        date = parse(text).date()
        all_matches[date].append(match)

    filtered_matches = filter_matches(all_matches)

    for date, matchList in filtered_matches.items():
        print(human(date))
        for i, match in enumerate(matchList):
            print(f"    {i+1}) {match['team1']} - {match['team2']}")
        print()

    driver.quit()