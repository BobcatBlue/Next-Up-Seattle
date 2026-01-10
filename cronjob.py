import requests
from datetime import datetime
import yaml
import selectorlib
import urllib.request
import json
from bs4 import BeautifulSoup


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

def getSoup(url):
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0'
        }
    )
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def scrape_central():
    venue = "Central Saloon"
    website = "http://www.centralsaloon.com"
    neighborhood = "Pioneer Square"
    url = "https://centralsaloon.com/music-events/"
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0'
        }
    )
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        event_tags = soup.find_all('h3', class_='mec-event-title')
        date_tags = soup.find_all('span', class_="mec-start-date-label")

        events = [item.text.replace(" • ", ", ") for item in event_tags[0:5]]
        dates_text = [item.text for item in date_tags[0:5]]
        days = [item[0:2] for item in dates_text]
        months = [item[3:] for item in dates_text]

        current_month = datetime.now().month
        current_year = datetime.now().year
        next_year = current_year + 1
        dates = []
        i = 0
        while i < 5:
            if current_month == 12 and months[i] == "Jan":
                year = next_year
            else:
                year = current_year
            date = f"{months[i]} {days[i]}, {year}"
            dates.append(date)
            i += 1


    except Exception:
        events = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, events, dates


def scrape_babayaga():
    venue = "Baba Yaga"
    website = "https://babayagaseattle.com/"
    neighborhood = "Pioneer Square"
    start_date = datetime.now()
    start_date = start_date.strftime("%Y-%m-%d")
    try:
        url = "https://www.venuepilot.co/graphql"
        data = {
            "operationName": None,
            "variables": {
                "accountIds": [2906],
                "startDate": start_date,
                "endDate": None,
                "search": "",
                "searchScope": "",
                "page": 1
            },
            "query": """
                query ($accountIds: [Int!]!, $startDate: String!, $endDate: String, $search: String, $searchScope: String, $limit: Int, $page: Int) {
                    paginatedEvents(arguments: {accountIds: $accountIds, startDate: $startDate, endDate: $endDate, search: $search, searchScope: $searchScope, limit: $limit, page: $page}) {
                        collection {
                            name
                            date
                        }
                    }
                }
                """
        }
        response = requests.post(url, json=data, headers=HEADERS)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            raw_calendar_data = response.json()
        else:
            print(f"Failed to fetch events: {response.status_code}")
            return "No Info", "--"

        # print(raw_calendar_data)

        today = datetime.now().strftime("%b %d, %Y")
        today = datetime.strptime(today, "%b %d, %Y")

        # The dates-list includes dates well before today's date
        # This code finds the index number for today's dates
        index_of_today = 0
        for event in raw_calendar_data["data"]["paginatedEvents"]["collection"]:
            date = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%b %d, %Y")
            date = datetime.strptime(date, "%b %d, %Y")

            if today > date:
                index_of_today += 1
            else:
                break

        # This is a list of dictionaries
        events_dictionaries = raw_calendar_data["data"]["paginatedEvents"]["collection"][
                              index_of_today:index_of_today + 5]

        bands = []
        unformatted_dates = []

        for item in events_dictionaries:
            bands.append(item["name"])
            unformatted_dates.append(item["date"])

        # Reformat the dates and put them in a new list
        dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y") for date in unformatted_dates]


    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_el_corazon():
    venue = "El Corazon"
    website = "https://elcorazonseattle.com/"
    neighborhood = "Capitol Hill"
    url = "https://elcorazonseattle.com/"
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0'
        }
    )
    try:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        el_corazon_calendar = soup.find("div", class_="el-corazon")
        headliner_tags = el_corazon_calendar.find_all("a", class_="link-block-3 no-underline w-inline-"
                                                                  "block w-condition-invisible")[0:5]
        headliners = [headliner.find("div", class_="headliners").text for headliner
                      in headliner_tags]
        supporting_acts = [support.text for support
                           in el_corazon_calendar.find_all("div", class_="supports")][0:5]
        bands = []
        for index, headliner in enumerate(headliners):
            if headliner == "":
                band = f"{supporting_acts[index]}"
            else:
                band = f"{headliner}, {supporting_acts[index]}"
            bands.append(band)

        day_dates = [date.find_all("div", class_="text-block-72") for date
                     in el_corazon_calendar.find_all("div", class_="day-date")][0:5]
        dates = [date[1].text for date in day_dates]
        current_month = datetime.now().month
        current_year = datetime.now().year
        next_year = current_year + 1
        for index, date in enumerate(dates):
            if date[0:3] == "Jan" and current_month == 12:
                date = f"{date}, {next_year}"
                dates[index] = date
            else:
                date = f"{date}, {current_year}"
                dates[index] = date

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_funhouse():
    venue = "Funhouse"
    website = "https://elcorazonseattle.com/"
    neighborhood = "Capitol Hill"
    url = "https://elcorazonseattle.com/"
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0'
        }
    )

    try:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        funhouse_calendar = soup.find("div", class_="funhouse")
        headliner_tags = funhouse_calendar.find_all("a", class_="link-block-3 no-underline w-inline-"
                                                                  "block w-condition-invisible")[0:5]
        headliners = [headliner.find("div", class_="headliners").text for headliner
                      in headliner_tags]
        supporting_acts = [support.text for support
                           in funhouse_calendar.find_all("div", class_="supports")][0:5]

        bands = []
        for index, headliner in enumerate(headliners):
            if headliner == "":

                band = f"{supporting_acts[index]}"
            else:
                band = f"{headliner}, {supporting_acts[index]}"
            bands.append(band)

        day_dates = [date.find_all("div", class_="text-block-72") for date
                     in funhouse_calendar.find_all("div", class_="day-date")][0:5]
        dates = [date[1].text for date in day_dates]
        current_month = datetime.now().month
        current_year = datetime.now().year
        next_year = current_year + 1
        for index, date in enumerate(dates):
            if date[0:3] == "Jan" and current_month == 12:
                date = f"{date}, {next_year}"
                dates[index] = date
            else:
                date = f"{date}, {current_year}"
                dates[index] = date
        # for band in bands:
        #     print(band)
        # print(dates)

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_nuemos():
    venue = "Nuemos"
    website = "https://www.nuemos.com/"
    neighborhood = "Capitol Hill"
    try:
        website = "https://www.neumos.com/events"
        response = requests.get(website, headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_nuemos.yaml")
        bands = extractor.extract(source)["bands"][0:5]
        dates = extractor.extract(source)["date"][0:5]
        current_month = datetime.now().month
        current_year = datetime.now().year
        next_year = current_year + 1

        for index, date in enumerate(dates):
            if date[0:3] == "Jan" and current_month == 12:
                date = f"{date}, {next_year}"
                dates[index] = date
            else:
                date = f"{date}, {current_year}"
                dates[index] = date

        # print(bands)
        # print(dates)

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    # print(bands)
    # print(dates)
    return venue, website, neighborhood, bands, dates


def scrape_showbox_presents():
    url = "https://www.showboxpresents.com"
    try:
        response = requests.get("https://www.showboxpresents.com/events/all", headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_showbox.yaml")
        events = extractor.extract(source)["event_name"][0:100]
        dates = extractor.extract(source)["date"][0:100]
        venues = extractor.extract(source)["venue"][0:100]

        counter = 0
        showbox_list = []
        showbox_sodo_list = []
        while counter < (len(events)):
            event = [venues[counter], events[counter], dates[counter]]
            match event[0]:
                case "@ Showbox SoDo":
                    showbox_sodo_list.append(event)
                case "@ The Showbox":
                    showbox_list.append(event)
                case _:
                    pass
            counter += 1

        showbox_list = showbox_list[0:5]
        showbox_sodo_list = showbox_sodo_list[0:5]

        showbox_dates = []
        showbox_bands = []
        for item in showbox_list:
            showbox_dates.append(item[2])
            showbox_bands.append(item[1])
        showbox_dates = [item[5:] for item in showbox_dates]

        showbox_sodo_dates = []
        showbox_sodo_bands = []
        for item in showbox_sodo_list:
            showbox_sodo_dates.append(item[2])
            showbox_sodo_bands.append(item[1])
        showbox_sodo_dates = [item[5:] for item in showbox_sodo_dates]

        showbox_shows = ["The Showbox at the Market", url, "Pike Place Market",
                         showbox_bands, showbox_dates]
        showbox_sodo_shows = ["The Showbox SODO", url, "SODO", showbox_sodo_bands,
                              showbox_sodo_dates]

    except Exception:
        showbox_shows = ["The Showbox at the Market",
                         url,
                         "Pike Place",
                         ["No info - Check venue website", "--", "--", "--", "--"],
                         ["--", "--", "--", "--", "--"]]
        showbox_sodo_shows = ["The Showbox SODO",
                              url,
                              "SODO",
                              ["No info - Check venue website", "--", "--", "--", "--"],
                              ["--", "--", "--", "--", "--"]]

    return showbox_shows, showbox_sodo_shows


def scrape_nectar():
    venue = "Nectar Lounge"
    url = "http://www.nectarlounge.com"
    neighborhood = "Fremont"
    try:
        # response = requests.get("https://highdiveseattle.com/e/calendar/", headers=HEADERS)
        response = requests.get("https://nectarlounge.com/events/calendar/", headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_nectar.yaml")
        bands = extractor.extract(source)["band"][0:5]
        dates = extractor.extract(source)["date"][0:5]
        dates = [datetime.strptime(item[4:], "%b %d %Y").strftime("%b %d, %Y") for item in dates]

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, url, neighborhood, bands, dates


def scrape_hidden_hall():
    venue = "Hidden Hall"
    url = "https://www.hiddenhall.com/"
    neighborhood = "Fremont"
    try:
        response = requests.get("https://nectarlounge.com/events/calendar/", headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("hidden_hall.yaml")
        bands = extractor.extract(source)["band"][0:5]
        dates = extractor.extract(source)["date"][0:5]
        dates = [datetime.strptime(item[4:], "%b %d %Y").strftime("%b %d, %Y") for item in dates]

        # print(bands)
        # print(dates)

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, url, neighborhood, bands, dates


def scrape_crocodile():
    venue = "The Crocodile"
    website = "https://www.thecrocodile.com/"
    neighborhood = "Belltown"
    venueId = "KovZpZA1vFtA"
    url = f"{URL_1}{venueId}{URL_2}{API_KEY}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        data = response.json()
        events = data["_embedded"]["events"]

        index = 0
        bands = []
        dates = []

        while index <= 4:
            band = events[index]["name"]
            date = events[index]["dates"]["start"]["localDate"]
            bands.append(band)
            dates.append(date)
            index += 1

        dates = [datetime.strptime(item, "%Y-%m-%d").strftime("%b %d, %Y") for item in dates]

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_madame_lous():
    venue = "Madame Lous"
    website = "https://www.thecrocodile.com/madame-lous"
    neighborhood = "Belltown"
    venueId = "KovZ917AYIq"
    url = f"{URL_1}{venueId}{URL_2}{API_KEY}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        data = response.json()
        events = data["_embedded"]["events"]

        index = 0
        bands = []
        dates = []

        while index <= 4:
            band = events[index]["name"]
            date = events[index]["dates"]["start"]["localDate"]
            bands.append(band)
            dates.append(date)
            index += 1

        dates = [datetime.strptime(item, "%Y-%m-%d").strftime("%b %d, %Y") for item in dates]

    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_tractor_tavern():
    venue = "Tractor Tavern"
    website = "https://tractortavern.com/"
    neighborhood = "Ballard"
    try:
        url = "https://tractortavern.com/"
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_tractor.yaml")
        bands = extractor.extract(source)["bands"][0:5]
        dates = extractor.extract(source)["dates"][0:5]
        dates = [item[0:6].strip() for item in dates]
        current_month = datetime.now().month
        current_year = datetime.now().year
        next_year = current_year + 1

        for index, date in enumerate(dates):
            if date[0:3] == "Jan" and current_month == 12:
                date = f"{date}, {next_year}"
                dates[index] = date
            else:
                date = f"{date}, {current_year}"
                dates[index] = date


    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_conor_byrne():
    venue = "Conor Byrne Pub"
    website = "https://www.conorbyrnepub.com/#/events"
    neighborhood = "Ballard"
    start_date = datetime.now()
    start_date = start_date.strftime("%Y-%m-%d")
    try:
        url = "https://www.venuepilot.co/graphql"
        data = {
            "operationName": None,
            "variables": {
                "accountIds": [194],
                "startDate": start_date,
                "endDate": None,
                "search": "",
                "searchScope": "",
                "page": 1
            },
            "query": """
                query ($accountIds: [Int!]!, $startDate: String!, $endDate: String, $search: String, $searchScope: String, $limit: Int, $page: Int) {
                    paginatedEvents(arguments: {accountIds: $accountIds, startDate: $startDate, endDate: $endDate, search: $search, searchScope: $searchScope, limit: $limit, page: $page}) {
                        collection {
                            name
                            date
                        }
                    }
                }
                """
        }

        response = requests.post(url, json=data, headers=HEADERS)

        if response.status_code == 200:
            raw_calendar_data = response.json()
        else:
            print(f"Failed to fetch events: {response.status_code}")
            return "No Info", "--"

        today = datetime.now().strftime("%b %d, %Y")
        today = datetime.strptime(today, "%b %d, %Y")

        # The dates-list includes dates well before today's date
        # This code finds the index number for today's dates
        index_of_today = 0
        for event in raw_calendar_data["data"]["paginatedEvents"]["collection"]:
            date = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%b %d, %Y")
            date = datetime.strptime(date, "%b %d, %Y")

            if today > date:
                index_of_today += 1
            else:
                break

        # print(raw_calendar_data["data"]["paginatedEvents"]["collection"])

        # This is a list of dictionaries
        events_dictionaries = raw_calendar_data["data"]["paginatedEvents"]["collection"][
                              index_of_today:index_of_today + 5]

        bands = []
        unformatted_dates = []

        for item in events_dictionaries:
            bands.append(item["name"])
            unformatted_dates.append(item["date"])


        # Reformat the dates and put them in a new list
        dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y") for date in
                 unformatted_dates]


    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_seamonster():
    venue = "Sea Monster Lounge"
    website = "https://www.seamonsterlounge.com/"
    neighborhood = "Wallingford"
    # try:
    url = "https://www.seamonsterlounge.com/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="wix-warmup-data")
    data = json.loads(script.string)

    # Retrieve the first 5 events with all their data
    first_five = data["appsWarmupData"]["140603ad-af8d-84a5-2c80-a0f60cb47351"]["widgetcomp-kx2nxyph"]["events"]["events"][0:5]

    # Parse out desired information from first 5 events
    bands = [event["title"] for event in first_five]
    dates_unformatted = [event["scheduling"]["startDateFormatted"] for event in first_five]
    dates = [datetime.strptime(date, "%B %d, %Y").strftime("%b %e, %Y") for date in dates_unformatted]


    # except Exception:
    #     bands = ["No info - Check venue website", "--", "--", "--", "--"]
    #     dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_neptune():
    url = "https://www.stgpresents.org/stg-venues/neptune-theatre/events/"
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0'
        }
    )
    response = requests.get(url, headers=headers)
    html = response.text
    print(html)


def scrape_royal_room():
    venue = "The Royal Room"
    website = "https://theroyalroomseattle.com/"
    neighborhood = "Columbia City"
    url = "https://theroyalroomseattle.com/events/"

    # Get and parse html data
    soup = getSoup(url)
    event_tags = soup.find_all("h3", class_="wpem-heading-text")
    month_tags = soup.find_all("div", class_="wpem-month")
    day_tags = soup.find_all("div", class_="wpem-date")
    events = [item.text for item in event_tags[0:5]]
    months = [item.text for item in month_tags[0:5]]
    days = [item.text for item in day_tags[0:5]]

    # Construct date strings
    dates = []
    x = 0   # counter
    while x < 5:
        if months[x] == "Jan" and datetime.now().month == 12:
            year = datetime.now().year + 1
        else:
            year = datetime.now().year
        dates.append(f"{months[x]} {days[x]}, {year}")
        x += 1

    return venue, website, neighborhood, events, dates


def scrape_egans():
    pass


def scrape_rendezvous():
    pass


def scrape_wamu():
    pass


if __name__ == "__main__":
    print(scrape_royal_room())
