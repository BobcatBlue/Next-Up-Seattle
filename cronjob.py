import requests
from datetime import datetime
import yaml
import selectorlib
import pandas as pd
from time import sleep
import csv


SHOW_DATA = []
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like '
                  'Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Extract the url components and API key from app.yaml
with open("app.yaml", "r") as file:
    DATA = yaml.safe_load(file)
    file.close()
API_KEY = DATA["env_variables"]["API_KEY"]
URL_1 = DATA["env_variables"]["URL_1"]
URL_2 = DATA["env_variables"]["URL_2"]


# Call the API to get event info for ticket-service venues
def get_shows(venue_name, venueId):
    url = f"{URL_1}{venueId}{URL_2}{API_KEY}"

    response = requests.get(url)
    show_data = response.json()
    try:
        """Find the next show/earliest date in the list"""
        all_events = show_data.get('_embedded').get('events')
        list_length = len(all_events)
        date_list = []
        counter = 0
        while counter < list_length:
            date = show_data.get('_embedded')['events'][counter].get('dates').get('start').get('localDate')
            date = datetime.strptime(date, "%Y-%m-%d")
            counter += 1
            date_list.append(date)
        earliest = min(date_list)
        earliest_index = date_list.index(earliest)


        show_events: list = show_data.get('_embedded').get('events')
        next_show = show_events[earliest_index]
        return venue_name, \
            next_show.get('name'), next_show.get('dates').get('start').get('localDate')


    except Exception:
        band = "No info"
        date = "No info"
        return venue_name, band, date


# Scrape the Central Saloon's calendar for the next show
def scrape_central():
    response = requests.get("https://www.centralsaloon.com/events", headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_central.yaml")
    band = extractor.extract(source)["band"][0]
    month = str(extractor.extract(source)["month"])
    day = extractor.extract(source)["day"]

    current_month = datetime.now().month
    if current_month == 12 and month == "Jan":
        year = "2025"
    else:
        year = datetime.now().year

    date = f"{month} {day}, {year}"
    return band, date


# Scrape El Corazon's website for their next show
def scrape_el_corazon():
    response = requests.get("https://elcorazonseattle.com/")
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_corazon.yaml")
    date = extractor.extract(source)["dates"][0]
    band = extractor.extract(source)["bands"][0]

    year_now = datetime.now().year
    month = datetime.now().month

    if month == 12 and month == 1:
        year = year_now + 1
    else:
        year = year_now
    date = f"{date} {year}"
    date = datetime.strptime(date, "%a %b %d %Y").strftime("%b %d, %Y")

    return band, date


# Scrape El Corazon's website for the next show at the Funhouse
def scrape_funhouse():
    response = requests.get("https://elcorazonseattle.com/")
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_funhouse.yaml")
    date = extractor.extract(source)["dates"][0]
    band = extractor.extract(source)["bands"][0]

    year_now = datetime.now().year
    month = datetime.now().month

    if month == 12 and month == 1:
        year = year_now + 1
    else:
        year = year_now
    date = f"{date} {year}"
    date = datetime.strptime(date, "%a %b %d %Y").strftime("%b %d, %Y")

    return band, date


# This one scrapes the Showbox website for multiple venues: Showbox, Showbox Sodo
def scrape_showbox_presents():
    response = requests.get("https://www.showboxpresents.com/events/all")
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_showbox.yaml")
    events = extractor.extract(source)["event_name"]
    dates = extractor.extract(source)["date"]
    venues = extractor.extract(source)["venue"]

    counter = 0
    showbox_list = []
    showbox_sodo_list = []
    while counter <= (len(events) - 1):
        event = [venues[counter], events[counter], dates[counter]]
        match event[0]:
            case "@ Showbox SoDo":
                showbox_sodo_list.append(event)
            case "@ The Showbox":
                showbox_list.append(event)
            case _:
                pass
        counter += 1

    showbox_show = showbox_list[0]
    showbox_show[2] = showbox_show[2][5:]
    showbox_show[0] = "The Showbox (@ the Market)"
    showbox_sodo_show = showbox_sodo_list[0]
    showbox_sodo_show[2] = showbox_sodo_show[2][5:]
    showbox_sodo_show[0] = "The Showbox SoDo"

    print(showbox_show, showbox_sodo_show)

    return showbox_show, showbox_sodo_show


def scrape_nectar():
    response = requests.get("https://highdiveseattle.com/e/calendar/", headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_nectar.yaml")
    band = extractor.extract(source)["band"][0]
    date = extractor.extract(source)["date"][0][4:]
    date = datetime.strptime(date, "%b %d %Y").strftime("%b %d, %Y")

    return band, date


def scrape_highdive():
    response = requests.get("https://highdiveseattle.com/e/calendar/", headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_highdive.yaml")
    band = extractor.extract(source)["band"][0]
    date = extractor.extract(source)["date"][0][4:]
    date = datetime.strptime(date, "%b %d %Y").strftime("%b %d, %Y")

    return band, date


"""
******************************************************
     The following code is for testing this page
******************************************************
"""


# Unused function for writing event info to a local CSV file
def call_shows():
    df = pd.read_csv("Listed_Venues.csv")
    print("Ring ring!!!  I'm inside call_shows(), calling the API")
    for index, row in df.iterrows():
        venue, band, date = get_shows(row["Venue Name"], row["vID"])
        if date == "No info":
            SHOW_DATA.append([venue, "No Info", "No Info"])
        else:
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
            SHOW_DATA.append([venue, band, date])
        sleep(0.09)

    with open("Show_Data.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(SHOW_DATA)


# This function is for testing "if __name__ "
def scrape_central_saloon():
    band, date = scrape_central()
    SHOW_DATA.append(["Central Saloon", band, date])



if __name__ == "__main__":
    scrape_highdive()

