import requests
from datetime import datetime
import yaml
import selectorlib


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


def scrape_central():
    venue = "Central Saloon"
    website = "http://www.centralsaloon.com"
    neighborhood = "Pioneer Square"
    try:
        response = requests.get("https://www.centralsaloon.com/events", headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("central.yaml")
        bands = extractor.extract(source)["bands"][0:5]
        months = extractor.extract(source)["months"][0:5]
        days = extractor.extract(source)["days"][0:5]
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
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


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
    try:
        response = requests.get("https://elcorazonseattle.com/", headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_corazon.yaml")
        dates = extractor.extract(source)["dates"][0:5]
        dates = [item[4:] for item in dates]
        bands = extractor.extract(source)["bands"][0:5]
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

    return venue, website, neighborhood, bands, dates


def scrape_funhouse():
    venue = "Funhouse"
    website = "https://elcorazonseattle.com/"
    neighborhood = "Capitol Hill"
    try:
        response = requests.get("https://elcorazonseattle.com/", headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_funhouse.yaml")
        dates = extractor.extract(source)["dates"][0:5]
        dates = [item[4:] for item in dates]
        bands = extractor.extract(source)["bands"][0:5]
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
        events = extractor.extract(source)["event_name"]
        dates = extractor.extract(source)["date"]
        venues = extractor.extract(source)["venue"]

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
                         ["No info - Check venue website", "--", "--", "--", "--"],
                         ["--", "--", "--", "--", "--"]]
        showbox_sodo_shows = ["The Showbox SODO",
                              url,
                              ["No info - Check venue website", "--", "--", "--", "--"],
                              ["--", "--", "--", "--", "--"],]

    return showbox_shows, showbox_sodo_shows


def scrape_nectar():
    venue = "Nectar Lounge"
    url = "http://www.nectarlounge.com"
    neighborhood = "Fremont"
    try:
        response = requests.get("https://highdiveseattle.com/e/calendar/", headers=HEADERS)
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
        response = requests.get("https://nectarlounge.com/", headers=HEADERS)
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
    url = "https://www.thecrocodile.com/"
    neighborhood = "Belltown"
    try:
        url = "https://www.ticketweb.com/venue/the-crocodile-seattle-wa/10352"
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("extract_crocodile.yaml")
        bands = extractor.extract(source)["bands"][0:5]
        dates = extractor.extract(source)["dates"][0:5]
        dates = [item[4:10].strip(" ") for item in dates]
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

    return venue, url, neighborhood, bands, dates


def scrape_madame_lous():
    venue = "Madame Lous"
    website = "https://www.thecrocodile.com/madame-lous"
    neighborhood = "Belltown"
    try:
        url = "https://www.ticketweb.com/venue/madame-lou-s-seattle-wa/497135"
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("madame_lous.yaml")
        bands = extractor.extract(source)["bands"][0:5]
        dates = extractor.extract(source)["dates"][0:5]
        dates = [item[4:10].strip(" ") for item in dates]
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

        print(bands)
        print(dates)


    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        print("Error")

    return venue, website, neighborhood, bands, dates


def scrape_conor_byrne():
    venue = "Conor Byrne Pub"
    website = "https://www.conorbyrnepub.com/#/events"
    neighborhood = "Ballard"
    start_date = datetime.now()
    start_date = start_date.strftime("%Y-%m-%d")
    print(start_date)
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
    try:
        url = "https://www.seamonsterlounge.com/"
        response = requests.get(url, HEADERS)
        response.encoding = 'utf-8'
        source = response.text
        extractor = selectorlib.Extractor.from_yaml_file("sea_monsters.yaml")
        bands = extractor.extract(source)["bands"][0:5]
        dates = extractor.extract(source)["dates"][0:5]
        dates = [item[5:] for item in dates]
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

    return venue, website, neighborhood, bands, dates


def scrape_egans():
    pass


def scrape_rendezvous():
    pass


def scrape_wamu():
    pass


if __name__ == "__main__":
    for item in scrape_hidden_hall():
        print(item)
