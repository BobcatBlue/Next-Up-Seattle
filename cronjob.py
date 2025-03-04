import requests
from datetime import datetime
import yaml
import selectorlib
import pandas as pd
from time import sleep
import csv
from collections import deque
import re


SHOW_DATA = []
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like '
                  'Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# UA = UserAgent()

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
        band = "No info - Check venue website"
        date = "--"
        return venue_name, band, date


# Scrape the Central Saloon's calendar for the next show
def scrape_central():
    response = requests.get("https://www.centralsaloon.com/events", headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("central.yaml")
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
    response = requests.get("https://elcorazonseattle.com/", headers=HEADERS)
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
    response = requests.get("https://elcorazonseattle.com/", headers=HEADERS)
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
    response = requests.get("https://www.showboxpresents.com/events/all", headers=HEADERS)
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


def scrape_crocodile():
    url = "https://www.ticketweb.com/venue/the-crocodile-seattle-wa/10352"
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_crocodile.yaml")
    annoying_string = extractor.extract(source)["band"]
    x = 67
    weekday = "zzz"
    while weekday not in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
        last_chars = deque(maxlen=x)
        for char in annoying_string:
            last_chars.append(char)
        double_date = "".join(last_chars)
        weekday = double_date[0:3]
        x += 1

    date = double_date[4:10].strip()
    month = datetime.now().month
    year = datetime.now().year
    if month == 12 and date[0:3] == "Jan":
        year += 1
    date = f"{date}, {str(year)}"
    dbl = len(annoying_string) - x
    double_band = annoying_string[0:dbl]
    b_length = int((dbl - 1)/2)
    band = double_band[0:b_length]

    return band, date


def scrape_madame_lous():
    url = "https://www.ticketweb.com/venue/madame-lou-s-seattle-wa/497135"
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("madame_lous.yaml")
    annoying_string = extractor.extract(source)["band"]
    x = 67
    weekday = "zzz"
    while weekday not in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
        last_chars = deque(maxlen=x)
        for char in annoying_string:
            last_chars.append(char)
        double_date = "".join(last_chars)
        weekday = double_date[0:3]
        x += 1

    date = double_date[4:10].strip()
    month = datetime.now().month
    year = datetime.now().year
    if month == 12 and date[0:3] == "Jan":
        year += 1
    date = f"{date}, {str(year)}"
    dbl = len(annoying_string) - x
    double_band = annoying_string[0:dbl]
    b_length = int((dbl - 1)/2)
    band = double_band[0:b_length]

    return band, date


def scrape_nuemos():
    url = "https://www.neumos.com/events"
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_nuemos.yaml")
    bands = extractor.extract(source)["bands"]
    print(bands)
    band = bands[0]
    date_list = extractor.extract(source)["date"]
    print(date_list)
    month = datetime.now().month
    if month == 12 and date_list[0][0:2] == "Jan":
        year = datetime.now().year + 1
    else:
        year = datetime.now().year
    date = f"{date_list[0]}, {year}"

    return band, date


def scrape_tractor_tavern():
    url = "https://tractortavern.com/"
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("extract_tractor.yaml")
    band = extractor.extract(source)["band"]
    month_day = extractor.extract(source)["date"][0][0:6]
    month = datetime.now().month
    if month == 12 and month_day[0:3] == "Jan":
        year = datetime.now().year + 1
    else:
        year = datetime.now().year
    date = f"{month_day}, {year}"

    return band, date


def scrape_egans():
    def remove_text_between(text, start, end):
        return re.sub(f'{re.escape(start)}.*?{re.escape(end)}', '', text)

    url = "https://www.ballardjamhouse.com/schedule.html"
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("egans.yaml")
    all_event_data = extractor.extract(source)["event"]

    removed_brackets = [remove_text_between(item, "[", "]") for item in all_event_data]
    removed_parenthesis = [remove_text_between(item, "(", ")") for item in removed_brackets]

    events = [item[10:].strip(" ") for item in removed_parenthesis]
    events = [item.strip("\r\n\r\n") for item in events]
    events = [item.strip("\r\n") for item in events]

    month_days = [item[4:10].strip(" ") for item in removed_parenthesis]

    if month_days[0][0:2] == "Dec" and datetime.now().month == 1:
        year = datetime.now().year + 1
    else:
        year = datetime.now().year

    dates = [datetime.strptime(f"{item}, {year}", "%b %d, %Y") for item in month_days]
    todays_date = datetime.now()
    for index, date in enumerate(dates):
        if todays_date < date:
            nxt_event_index = index
            break

    date = datetime.strftime(dates[nxt_event_index], "%b %d, %Y")
    event = events[nxt_event_index]

    print("Egans")

    return event, date


def scrape_seamonster():
    try:
        url = "https://www.seamonsterlounge.com/"
        response = requests.get(url, HEADERS)
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("sea_monsters.yaml")
        band = extractor.extract(source)["band"]
        day = extractor.extract(source)["date"][5:]
        if day[0:3] == "Jan" and datetime.now().month == 12:
            year = datetime.now().year + 1
        else:
            year = datetime.now().year
        date = f"{day}, {year}"
    except Exception:
        band = "No Info - Check venue's FB or Insta for upcoming shows"
        date = "--"

    print(band, date)
    return band, date


def scrape_wamu():
    url = "https://www.wamutheater.com/event-calendar?category=All+Events"
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file("wamu.yaml")
    band = extractor.extract(source)["band"]
    day = extractor.extract(source)["date"]
    if day[0:3] == "Jan" and datetime.now().month == 12:
        year = datetime.now().year + 1
    else:
        year = datetime.now().year
    date = f"{day}, {year}"

    print("WAMU")
    return band, date


def scrape_rendezvous():
    pass


def scrape_babayaga():
    url = "https://www.venuepilot.co/graphql"
    data = {
        "operationName": None,
        "variables": {
            "accountIds": [2906],
            "startDate": "2025-03-04",
            "endDate": None,
            "search": "",
            "searchScope": "",
            "page": 1
        },
        "query": """
            query ($accountIds: [Int!]!, $startDate: String!, $endDate: String, $search: String, $searchScope: String, $limit: Int, $page: Int) {
                paginatedEvents(arguments: {accountIds: $accountIds, startDate: $startDate, endDate: $endDate, search: $search, searchScope: $searchScope, limit: $limit, page: $page}) {
                    collection {
                        id
                        name
                        date
                        doorTime
                        startTime
                        endTime
                        minimumAge
                        promoter
                        support
                        description
                        websiteUrl
                        twitterUrl
                        instagramUrl
                        ...AnnounceImages
                        status
                        announceArtists {
                            applemusic
                            bandcamp
                            facebook
                            instagram
                            lastfm
                            name
                            songkick
                            spotify
                            twitter
                            website
                            wikipedia
                            youtube
                            __typename
                        }
                        artists {
                            bio
                            createdAt
                            id
                            name
                            updatedAt
                            __typename
                        }
                        venue {
                            name
                            __typename
                        }
                        footerContent
                        ticketsUrl
                        __typename
                    }
                    metadata {
                        currentPage
                        limitValue
                        totalCount
                        totalPages
                        __typename
                    }
                    __typename
                }
            }

            fragment AnnounceImages on PublicEvent {
                announceImages {
                    name
                    highlighted
                    versions {
                        thumb {
                            src
                            __typename
                        }
                        cover {
                            src
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
            """
    }
    response = requests.post(url, json=data, headers=HEADERS)

    if response.status_code == 200:
        raw_calendar_data = response.json()
        print(raw_calendar_data)
    else:
        print(f"Failed to fetch events: {response.status_code}")
        return "No Info", "--"

    event = raw_calendar_data["data"]["paginatedEvents"]["collection"][0]
    print(event)
    band = event["name"]
    date = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%b %d, %Y")

    print(band)
    print(date)
    return band, date


# This function doesn't work yet
def scrape_conor_byrne():
    url = "https://www.venuepilot.co/graphql"
    data = {
        "operationName":None,
        "variables": {
            "accountIds": [194],
            "startDate": "2025-03-04",
            "endDate": None,
            "search": "",
            "searchScope": "",
            "page" :1
        },
        "query":"""
            query ($accountIds: [Int!]!, $startDate: String!, $endDate: String, $search: String, $searchScope: String, $limit: Int, $page: Int) {
                paginatedEvents(arguments: {accountIds: $accountIds, startDate: $startDate, endDate: $endDate, search: $search, searchScope: $searchScope, limit: $limit, page: $page}) {
                    collection {
                        id
                        name
                        date
                        doorTime
                        startTime
                        endTime
                        minimumAge
                        promoter
                        support
                        description
                        websiteUrl
                         twitterUrl
                        instagramUrl
                        ...AnnounceImages
                        status
                        announceArtists {
                            applemusic
                            bandcamp
                            facebook
                            instagram
                            lastfm
                            name
                            songkick
                            spotify
                            twitter
                            website
                            wikipedia
                            youtube
                            __typename
                        }
                        artists {
                        bio
                       createdAt
                        id
                        name
                        updatedAt
                         __typename
                        }
                        venue {        
                            name        
                            __typename      
                        }     
                        footerContent      
                        ticketsUrl
                        __typename
                    }
                    metadata {
                        currentPage
                        limitValue
                        totalCount 
                        totalPages 
                        __typename
                    }
                    __typename
                }
            }
                
            fragment AnnounceImages on PublicEvent {
                announceImages {
                    name
                    highlighted
                    versions {
                        thumb {
                            src
                            __typename
                        }   
                        cover {
                            src   
                            __typename
                        }
                    __typename
                }
                __typename
            }
        __typename
        }
    """
    }

    response = requests.post(url, json=data, headers=HEADERS)

    if response.status_code == 200:
        raw_calendar_data = response.json()
    else:
        print(f"Failed to fetch events: {response.status_code}")
        return "No Info", "--"

    event = raw_calendar_data["data"]["paginatedEvents"]["collection"][0]
    print(event)
    band = event["name"]
    date = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%b %d, %Y")

    print(band)
    print(date)

    return band, date




# def scrape_climate_pledge():
#     try:
#         url = "https://www.climatepledgearena.com/events/category/concerts/"
#         response = requests.get(url, headers={'User-Agent': UA.firefox})
#         source = response.text
#         extractor = selectorlib.Extractor.from_yaml_file("climate_pledge.yaml")
#         band = extractor.extract(source)["band"]
#         day = extractor.extract(source)["date"]
#         day = day.split("/")[0].strip(" ")
#         if day[0:2] == "Jan" and datetime.now().month == 12:
#             year = datetime.now().year + 1
#         else:
#             year = datetime.now().year
#         date = datetime.strptime(f"{day}, {year}", "%B %d, %Y")
#         date = datetime.strftime(date, "%b %d, %Y")
#         return band, date
#     except Exception:
#         return "No info. Check venue website directly.", "-"


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
    scrape_conor_byrne()
