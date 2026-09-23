import datetime
from dateutil.relativedelta import relativedelta
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import yaml
import selectorlib
import json
from bs4 import BeautifulSoup
import pprint

"""
============================
     GLOBALS 'N' STUFF
============================
"""

PACIFIC = ZoneInfo("America/Los_Angeles")
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



"""
============================
    USEFUL FUNCTIONS
============================
"""


def get_soup(url):
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


def strip_full_days(some_string: str):
    days_list = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    final_string = some_string
    for day in days_list:
        if day in some_string:
            string_1 = some_string.replace(day, "")
            final_string = string_1.replace(",", "").strip()
            break
        else:
            continue
    final_string = final_string.replace(".", "")
    return final_string


def request_json(url: str):
    headers = HEADERS
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    data = response.json()
    return data


def extract_json_from_script(script_text):
    if not script_text:
        return None

    start = script_text.find("{")
    end = script_text.rfind("}")

    if start == -1 or end == -1:
        return None

    json_str = script_text[start:end + 1]

    return json.loads(json_str)


def add_years(dates_no_years):
    dates = dates_no_years
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
    return dates


def dtzip_12hr(dates, times):
    date_tuples = list(zip(dates, times))
    # print(date_tuples)
    iso_dates = []
    for datetime_string in date_tuples:
        dt = datetime.strptime(f"{datetime_string[0]} {datetime_string[1]}",
                               "%b %d, %Y %I:%M %p")
        dt = dt.replace(tzinfo=PACIFIC)
        iso_dates.append(dt.isoformat())
    return iso_dates


def dtzip_24hr(dates, times):
    date_tuples = list(zip(dates, times))
    # print(date_tuples)
    iso_dates = []
    for datetime_string in date_tuples:
        dt = datetime.strptime(f"{datetime_string[0]} {datetime_string[1]}",
                               "%b %d, %Y %H:%M:%S")
        dt = dt.replace(tzinfo=PACIFIC)
        iso_dates.append(dt.isoformat())
    return iso_dates


"""
==============================
      SCRAPING MODULES
==============================
"""

"""
List of modules to migrate off of the YAML method:
- Neumos
- Showboxes
- Tractor Tavern

"""


def scrape_central():
    venue = "Central Saloon"
    website = "http://www.centralsaloon.com"
    neighborhood = "Pioneer Square"
    url = "https://centralsaloon.com/music-events/"

    try:
        soup = get_soup(url)

        # Find tags for events, dates, times, and ticket links
        event_tags = soup.find_all('h3', class_='mec-event-title')
        date_tags = soup.find_all('span', class_="mec-start-date-label")
        time_tags = soup.find_all('span', class_="mec-start-time")
        ticket_link_div_tags = soup.find_all('div', class_="mec-event-image")

        # Extract text from tags for events, dates, times and ticket links
        events = [item.text.replace(" • ", ", ") for item in event_tags[0:5]]
        dates_text = [item.text for item in date_tags[0:5]]
        times = [item.text for item in time_tags[0:5]]
        ticket_links = []
        for tag in ticket_link_div_tags[0:5]:
            a = tag.find("a", href=True)
            ticket_links.append(a["href"])
            # print(a["href"])

        days = []
        months = []
        for date in dates_text:
            if "-" in date:
                days.append(date[0:2])
                months.append(date[8:])
            else:
                days.append(date[0:2])
                months.append(date[3:])

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

        iso_dates = dtzip_12hr(dates, times)

    except Exception:
        events = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://centralsaloon.com/music-events/",
                        "https://centralsaloon.com/music-events/",
                        "https://centralsaloon.com/music-events/",
                        "https://centralsaloon.com/music-events/",
                        "https://centralsaloon.com/music-events/"]

    return venue, website, neighborhood, events, dates, iso_dates, ticket_links


def scrape_babayaga():
    venue = "Baba Yaga"
    website = "https://babayagaseattle.com/seattle-pioneer-square-baba-yaga-events-days#/events"
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
                            startTime
                            ticketsUrl
                            description
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
        todays_index = 0
        for event in raw_calendar_data["data"]["paginatedEvents"]["collection"]:
            date = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%b %d, %Y")
            date = datetime.strptime(date, "%b %d, %Y")

            if today > date:
                todays_index += 1
            else:
                break

        # This is a list of dictionaries
        event_data = raw_calendar_data["data"]["paginatedEvents"]["collection"][
                              todays_index:todays_index + 5]

        bands = []
        unformatted_dates = []
        times = []
        iso_dates = []
        ticket_urls = []

        for item in event_data:
            bands.append(item["name"])
            unformatted_dates.append(item["date"])
            times.append(item["startTime"])
            ticket_urls.append(item["ticketsUrl"])
        # Reformat the dates and put them in a new list
        dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y") for date in unformatted_dates]
        dt_tuples = list(zip(dates, times))
        # print(dt_tuples)
        for pair in dt_tuples:
            dt = datetime.strptime(f"{pair[0]} {pair[1]}",
                                   "%b %d, %Y %H:%M:%S")
            dt = dt.replace(tzinfo=PACIFIC)
            iso_dates.append(dt.isoformat())


    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_urls = ["https://babayagaseattle.com/seattle-pioneer-square-baba-yaga-events-days#/events",
                       "https://babayagaseattle.com/seattle-pioneer-square-baba-yaga-events-days#/events",
                       "https://babayagaseattle.com/seattle-pioneer-square-baba-yaga-events-days#/events",
                       "https://babayagaseattle.com/seattle-pioneer-square-baba-yaga-events-days#/events",
                       "https://babayagaseattle.com/seattle-pioneer-square-baba-yaga-events-days#/events"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_urls


def scrape_el_corazon():
    venue = "El Corazon"
    website = "https://elcorazonseattle.com/"
    neighborhood = "Capitol Hill"

    try:
        url = "https://elcorazonseattle.com/"
        soup = get_soup(url)
        el_corazon_calendar = soup.find("div", class_="el-corazon")
        headliners = [headliner.find("div", class_="headliners").text
                      for headliner in
                      el_corazon_calendar.find_all("a", class_="link-block-3 no-underline "
                                                                  "w-inline-block w-condition-"
                                                                  "invisible")[0:5]]
        supporting_acts = [support.text
                           for support in
                           el_corazon_calendar.find_all("div", class_="supports")][0:5]

        times = [showtime.find_all("div", class_="text-block-75")[4].text
                      for showtime in
                      el_corazon_calendar.find_all("div", class_="show-times")[0:5]]

        ticket_links = [f"www.elcorazonseattle.com{a['href']}"
                       for a in
                       el_corazon_calendar.find_all("a", class_="uui-button w-inline-block")[0:5]]

        # Concatenate strings for headliners and supporting acts into bands[]
        bands = []
        for index, headliner in enumerate(headliners):
            if headliner == "":
                band = f"{supporting_acts[index]}"
            else:
                band = f"{headliner}, {supporting_acts[index]}"
            bands.append(band)

        # This block creates a list of 2-item lists made of a weekday ("Sun") and date ("May 17")
        day_dates = [date.find_all("div", class_="text-block-72") for date
                     in el_corazon_calendar.find_all("div", class_="day-date")][0:5]

        # Extract month and day into a list
        dates_no_year = [date[1].text for date in day_dates]
        dates = add_years(dates_no_year)

        iso_dates = dtzip_12hr(dates, times)

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_funhouse():
    venue = "Funhouse"
    website = "https://elcorazonseattle.com/"
    neighborhood = "Capitol Hill"

    try:
        url = "https://elcorazonseattle.com/"
        soup = get_soup(url)
        funhouse_calendar = soup.find("div", class_="funhouse")
        headliner_tags = funhouse_calendar.find_all("a",
                                                    class_="link-block-3 no-underline w-inline-"
                                                           "block w-condition-invisible")[0:5]

        headliners = [headliner.find("div", class_="headliners").text
                      for headliner in
                      headliner_tags]

        supporting_acts = [support.text
                           for support in
                           funhouse_calendar.find_all("div", class_="supports")][0:5]

        times = [showtime.find_all("div", class_="text-block-75")[4].text
                      for showtime in
                      funhouse_calendar.find_all("div", class_="show-times")[0:5]]

        ticket_links = [f"www.elcorazonseattle.com{a['href']}"
                       for a in
                       funhouse_calendar.find_all("a", class_="uui-button w-inline-block")[0:5]]


        bands = []
        for index, headliner in enumerate(headliners):
            if headliner == "":

                band = f"{supporting_acts[index]}"
            else:
                band = f"{headliner}, {supporting_acts[index]}"
            bands.append(band)

        day_dates = [date.find_all("div", class_="text-block-72") for date
                     in funhouse_calendar.find_all("div", class_="day-date")][0:5]

        dates_no_year = [date[1].text for date in day_dates]
        dates = add_years(dates_no_year)

        iso_dates = dtzip_12hr(dates, times)


    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/",
                        "https://elcorazonseattle.com/"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_neumos():
    venue = "Neumos"
    website = "https://www.nuemos.com/"
    neighborhood = "Capitol Hill"
    try:
        url = "https://www.neumos.com/events"
        soup = get_soup(url)

        bands = [band.text for band in soup.find_all("a", title="More Info")[0:5]]
        date_tuples = [date.find_all("span")
                       for date in
                       soup.find_all("span", class_="m-date__singleDate")[0:5]]
        dates_no_year = [f"{date[0].text.strip()[0:3]} {date[1].text}" for date in date_tuples]
        dates = add_years(dates_no_year)
        times = [time.text.strip()[7:] for time in soup.find_all("div", class_="time")[0:5]]
        iso_dates = dtzip_12hr(dates, times)
        ticket_links = [a["href"] for a in soup.find_all("a", class_="tickets onsalenow")[0:5]]

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://www.neumos.com/events",
                        "https://www.neumos.com/events",
                        "https://www.neumos.com/events",
                        "https://www.neumos.com/events",
                        "https://www.neumos.com/events"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_barboza():
    venue = "Barboza"
    website = "https://www.thebarboza.com/events"
    neighborhood = "Capitol Hill"
    url = website
    try:
        soup = get_soup(url)

        bands = [band.text for band in soup.find_all("a", title="More Info")[0:5]]
        date_tuples = [date.find_all("span")
                       for date in
                       soup.find_all("span", class_="m-date__singleDate")[0:5]]
        dates_no_year = [f"{date[0].text.strip()[0:3]} {date[1].text}" for date in date_tuples]
        dates = add_years(dates_no_year)
        times = [time.text.strip()[7:] for time in soup.find_all("div", class_="time")[0:5]]
        iso_dates = dtzip_12hr(dates, times)
        ticket_links = [a["href"] for a in soup.find_all("a", class_="tickets onsalenow")[0:5]]

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://www.thebarboza.com/events",
                        "https://www.thebarboza.com/events",
                        "https://www.thebarboza.com/events",
                        "https://www.thebarboza.com/events",
                        "https://www.thebarboza.com/events"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_showbox_presents():
    url = "https://www.showboxpresents.com"
    try:
        soup = get_soup(url)
        # print(soup)
        event_cards = soup.find_all("div", class_="entry")
        # print(event_cards)

        showbox_bands = []
        showbox_dates = []
        showbox_times = []
        showbox_links = []

        sodo_bands = []
        sodo_dates = []
        sodo_times = []
        sodo_links = []

        for card in event_cards:
            match card.find("div", class_="event_venue").text:
                case "The Showbox":
                    if len(showbox_bands) == 5:
                        pass
                    showbox_bands.append(card.select_one("h3.carousel_item_title_small a").text.strip())
                    showbox_dates.append(card.find("div", class_="date").text.strip())
                    showbox_links.append(card.find("a", class_="tickets")["href"])

                case "Showbox SoDo":
                    if len(sodo_bands) == 5:
                        pass
                    sodo_bands.append(card.select_one("h3.carousel_item_title_small a").text.strip())
                    sodo_dates.append(card.find("div", class_="date").text.strip())
                    sodo_links.append(card.find("a", class_="tickets")["href"])

        for index, date in enumerate(showbox_dates):
            parts = date.split(' ')
            parts[0] = parts[0].strip(',')
            result = [' '.join(parts[1:4]), ' '.join(parts[4:])]
            showbox_dates[index] = result[0]
            showbox_times.append(result[1])

        for index, date in enumerate(sodo_dates):
            parts = date.split(' ')
            parts[0] = parts[0].strip(',')
            result = [' '.join(parts[1:4]), ' '.join(parts[4:])]
            sodo_dates[index] = result[0]
            sodo_times.append(result[1])

        showbox_iso_dates = dtzip_12hr(showbox_dates, showbox_times)
        sodo_iso_dates = dtzip_12hr(sodo_dates, sodo_times)

        showbox_info = ["The Showbox at the Market",
                        url,
                        "Downtown",
                        showbox_bands[0:5],
                        showbox_dates[0:5],
                        showbox_iso_dates[0:5],
                        showbox_links[0:5]]
        sodo_info = ["Showbox Sodo",
                     url,
                     "SODO",
                     sodo_bands[0:5],
                     sodo_dates[0:5],
                     sodo_iso_dates[0:5],
                     sodo_links[0:5]]

    except Exception:
        showbox_info = ["The Showbox at the Market",
                         url,
                         "Downtown",
                         ["No info - Click the venue name for info", "--", "--", "--", "--"],
                         ["--", "--", "--", "--", "--"],
                         ["--", "--", "--", "--", "--"],
                         ["", "", "", "", ""]]

        sodo_info = ["The Showbox SODO",
                              url,
                              "SODO",
                              ["No info - Click the venue name for info", "--", "--", "--", "--"],
                              ["--", "--", "--", "--", "--"],
                              ["--", "--", "--", "--", "--"],
                              ["", "", "", "", ""]]

    return showbox_info, sodo_info


def scrape_nectar():
    venue = "Nectar Lounge"
    website = "https://nectarlounge.com/events/calendar/"
    neighborhood = "Fremont"
    url = "https://nectarlounge.com/events/calendar/"
    try:
        soup = get_soup(url)
        event_elements = soup.find_all("div", attrs={"data-venue-id": "2376"})
        months = [item.find("span", attrs={"class": "sg-events__event-month"}).text
                  for item in event_elements[0:5]]
        days = [item.find("span", attrs={"class": "sg-events__event-day"}).text
                for item in event_elements[0:5]]
        years = [item.find("span", attrs={"class": "sg-events__event-year"}).text
                 for item in event_elements[0:5]]
        bands = [item.find("a", attrs={"class": "sg-events__event-title-link"}).text.strip()
                 for item in event_elements[0:5]]
        times = [item.find("time", class_="sg-events__event-start").text.strip()
                 for item in event_elements[0:5]]
        ticket_links = [item.find("a", class_="sg-events__event-ticket-link")["href"]
                        for item in event_elements[0:5]]
        dates = []
        for month, day, year in zip(months, days, years):
            dates.append(f"{month} {day}, {year}")

        iso_dates = dtzip_12hr(dates, times)

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_hidden_hall():
    venue = "Hidden Hall"
    website = "https://hiddenhall.com/"
    neighborhood = "Fremont"
    url = "https://nectarlounge.com/events/calendar/"
    try:
        soup = get_soup(url)
        event_elements = soup.find_all("div", attrs={"data-venue-id": "8386"})
        months = [item.find("span", attrs={"class": "sg-events__event-month"}).text
                  for item in event_elements[0:5]]
        days = [item.find("span", attrs={"class": "sg-events__event-day"}).text
                for item in event_elements[0:5]]
        years = [item.find("span", attrs={"class": "sg-events__event-year"}).text
                 for item in event_elements[0:5]]
        bands = [item.find("a", attrs={"class": "sg-events__event-title-link"}).text.strip()
                 for item in event_elements[0:5]]
        times = [item.find("time", class_="sg-events__event-start").text
                 for item in event_elements[0:5]]
        ticket_links = [item.find("a", class_="sg-events__event-ticket-link")["href"]
                        for item in event_elements[0:5]]
        dates = []
        for month, day, year in zip(months, days, years):
            dates.append(f"{month} {day}, {year}")

        iso_dates = dtzip_12hr(dates, times)

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/",
                        "https://nectarlounge.com/events/calendar/"]


    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_crocodile():
    venue = "The Crocodile"
    website = "https://www.thecrocodile.com/"
    neighborhood = "Belltown"
    url = "https://calendar.thecrocodile.com/"

    try:
        soup = get_soup(url)
        event_tags = [event for event in soup.find_all("a", class_="link-block-2")
                      if "w-condition-invisible" not in event.get("class")]

        croc_counter = 0
        croc_indices = []
        bands = []
        dates = []


        for index, event_tag in enumerate(event_tags):
            if croc_counter > 4:
                break
            else:
                venue_wrapper = event_tag.find("div", class_="venue-blcok uui-event_time-wrapper")
                the_venue = venue_wrapper.find( "div", class_="text-block-71 cal-start-date").text

                if the_venue == "The Crocodile":
                    croc_counter += 1
                    croc_indices.append(index)
                    bands.append(event_tag.find("h3", class_="uui-heading-xxsmall-2").text)
                    date_wrapper = event_tag.find("div",
                                                  class_="date-range-block uui-event_time-wrapper")
                    date_text = date_wrapper.find("div", class_="text-block-71 cal-start-date").text
                    month = date_text[0:3]
                    day = date_text.split(',', 1)[0][-2:]
                    year = date_text.split(',', 1)[1].strip()[0:4]
                    dates.append(f"{month} {day}, {year}")

        """The follwoing comment code is to be used later on for getting individual event times.
            You will have to scrape event pages individually, and use two different sites:
            the Crocodile's... and TicketWeb :(  """

        iso_dates = ["--", "--", "--", "--", "--"]

        url_prefix = "https://calendar.thecrocodile.com"
        for index in croc_indices:
            ticket_links = event_tags[index].get("href")
            if ticket_links[0:4] != "http":
                ticket_links = f"{url_prefix}{ticket_links}"
            new_soup = get_soup(ticket_links)

        #     if "ticketweb" in href:
        #         time_text = soup.find_all("div", class_="text-block-71 cal-start-date")
        #         print(new_soup)
        #         # for time in time_text:
        #         #     print(time)
        #     else:
        #         pass
        #
        # for band, date in zip(bands, dates):
        #     print(date, band)

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["", "", "", "", ""]

    return venue, website, neighborhood, bands, dates


""" This module is decommissioned

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
"""


def scrape_tractor_tavern():
    venue = "Tractor Tavern"
    website = "https://tractortavern.com/"
    neighborhood = "Ballard"
    try:
        url = "https://tractortavern.com/"
        soup = get_soup(url)
        bands = [band.text for band in soup.find_all("span", class_="artisteventsname")[0:5]]
        days_and_times = [daytime.text.split("@")
                          for daytime in soup.find_all("span", class_="artisteventstime")[0:5]]
        dates_no_years = [day[0].strip() for day in days_and_times]
        times = [time[1].strip() for time in days_and_times]
        ticket_links = [a["href"]
                        for a in
                        soup.select("div.eventsbutton a.button")[0:5]]

        dates = add_years(dates_no_years)
        iso_dates = dtzip_12hr(dates, times)

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://tractortavern.com/",
                        "https://tractortavern.com/",
                        "https://tractortavern.com/",
                        "https://tractortavern.com/",
                        "https://tractortavern.com/"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


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
                            startTime
                            ticketsUrl
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
        todays_index = 0
        for event in raw_calendar_data["data"]["paginatedEvents"]["collection"]:
            date = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%b %d, %Y")
            date = datetime.strptime(date, "%b %d, %Y")

            if today > date:
                todays_index += 1
            else:
                break

        # This is a list of dictionaries
        events_dictionaries = raw_calendar_data["data"]["paginatedEvents"]["collection"][
                              todays_index:todays_index + 5]

        bands = []
        unformatted_dates = []
        times = []
        ticket_links = []

        for item in events_dictionaries:
            bands.append(item["name"])
            unformatted_dates.append(item["date"])
            times.append(item["startTime"])
            if item["ticketsUrl"] is None:
                ticket_links.append("")
            else:
                ticket_links.append(item["ticketsUrl"])



        # Reformat the dates and put them in a new list
        dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y") for date in
                 unformatted_dates]

        iso_dates = dtzip_24hr(dates, times)


    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
        iso_dates = ["--", "--", "--", "--", "--"]
        ticket_links = ["https://www.conorbyrnepub.com/#/events",
                        "https://www.conorbyrnepub.com/#/events",
                        "https://www.conorbyrnepub.com/#/events",
                        "https://www.conorbyrnepub.com/#/events",
                        "https://www.conorbyrnepub.com/#/events"]

    return venue, website, neighborhood, bands, dates, iso_dates, ticket_links


def scrape_seamonster():
    venue = "Sea Monster Lounge"
    website = "https://www.seamonsterlounge.com/"
    neighborhood = "Wallingford"
    try:
        url = "https://www.seamonsterlounge.com/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="wix-warmup-data")
        data = json.loads(script.string)

        # Retrieve the first 5 events with all their data
        events = data["appsWarmupData"]["140603ad-af8d-84a5-2c80-a0f60cb47351"]["widgetcomp-kx2nxyph"]["events"]["events"][0:5]

        # Parse out desired information from first 5 events
        bands = [event["title"] for event in events]
        dates_unformatted = [event["scheduling"]["startDateFormatted"] for event in events]
        dates = [datetime.strptime(date, "%B %d, %Y").strftime("%b %e, %Y") for date in dates_unformatted]


    except Exception:
        bands = ["No info - Check venue website", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_neptune():
    venue = "The Neptune Theater"
    website = "https://www.stgpresents.org/stg-venues/neptune-theatre/events/"
    neighborhood = "University District"
    url = "https://www.stgpresents.org/stg-venues/neptune-theatre/events/"

    try:
        soup = get_soup(url)
        event_tags = soup.find_all("a", class_="mec-color-hover")
        date_tags = soup.find_all("div", class_="mec-event-description")
        bands = [event.text for event in event_tags[0:5]]
        dates_unformatted = [list(info.stripped_strings) for info in date_tags]
        dates = []
        for date_list in dates_unformatted[0:5]:
            date = date_list[1]
            dates.append(strip_full_days(date))

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_royal_room():
    venue = "The Royal Room"
    website = "https://theroyalroomseattle.com/"
    neighborhood = "Columbia City"
    url = "https://theroyalroomseattle.com/events/"

    try:
        # Get and parse html data
        soup = get_soup(url)
        event_tags = soup.find_all("h3", class_="wpem-heading-text")
        month_tags = soup.find_all("div", class_="wpem-month")
        day_tags = soup.find_all("div", class_="wpem-date")
        bands = [item.text for item in event_tags[0:5]]
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

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_substation():
    venue = "Substation Seattle"
    neighborhood = "Fremont"
    website = "https://www.substationseattle.com/"
    url = "https://www.eventbrite.com/o/substation-18831550522"
    try:
        soup = get_soup(url)
        scripts = soup.find_all("script")
        data = None
        for script in scripts:
            if script.string and "upcomingEvents" in script.string:
                data = extract_json_from_script(script.string)
                break
        events_raw = data["props"]["pageProps"]["upcomingEvents"]
        bands = [event["name"] for event in events_raw[0:5]]
        dates = [datetime.strptime(event["start_date"], "%Y-%m-%d").strftime("%b %d, %Y")
                 for event in events_raw[0:5]]
    # print(bands)
    # print(dates)

    # data = json.loads(event_script.string)
    # raw_event_data = data["itemListElement"]
    # bands = [item["item"]["name"] for item in raw_event_data[0:5]]
    # raw_dates = [item["item"]["startDate"][0:10] for item in raw_event_data[0:5]]
    # dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y") for date in raw_dates]

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_sunset_tavern():
    venue = "Sunset Tavern"
    website = "https://sunsettavern.com/shows/"
    neighborhood = "Ballard"
    url = "https://partners-endpoint.dice.fm/api/v2/events?page%5Bsize%5D=&types=linkout%2Cevent" \
          "&filter%5Bpromoters%5D%5B%5D=Bars+We+Like%2C+Inc+dba+Sunset+Tavern"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like "
                      "Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://sunsettavern.com",
        "Referer": "https://sunsettavern.com",
        "X-Api-Key": "uZgJttkg0G75xfWU7xCDI7nOQO9xhwAH4mC9xjr3"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()["data"]
        bands = [event["name"] for event in data[0:5]]
        dates_unformatted = [event["date"].split("T")[0] for event in data[0:5]]
        dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
                 for date in dates_unformatted]

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_bluemoon():
    venue = "The Blue Moon Tavern"
    website = "https://www.thebluemoonseattle.com/"
    neighborhood = "Wallingford"
    today = datetime.today().strftime("%Y-%m-%d")
    next_month = (datetime.today() + relativedelta(months=1)).strftime("%Y-%m-%d")
    # print(next_month)
    url = "https://clients6.google.com/calendar/v3/calendars/k3bcrptn7frodqrcbe093i3s4o%40group." \
          "calendar.google.com/events?calendarId=k3bcrptn7frodqrcbe093i3s4o%40group.calendar." \
          "google.com&singleEvents=true&eventTypes=default&eventTypes=focusTime&eventTypes=" \
          "outOfOffice&timeZone=America%2FLos_Angeles&maxAttendees=1&maxResults=250&sanitizeHtml=" \
          f"true&timeMin={today}T00%3A00%3A00-08%3A00&timeMax={next_month}T00%3A00%3A00-18%3A00&" \
          "&key=AIzaSyDOtGM5jr8bNp1utVpG2_gSRH03RNGBkI8&%24unique" \
          "=gc237"

    try:
        response = requests.get(url, headers=HEADERS)
        raw_calendar_data = response.json()["items"]
        # print(raw_calendar_data)
        event_names = [item["summary"] for item in raw_calendar_data]
        start_date_strings = [item["start"]["dateTime"] for item in raw_calendar_data]
        start_datetime_objects = [datetime.strptime(item, "%Y-%m-%dT%H:%M:%S%z")
                                  for item in start_date_strings]
        zipped_list = zip(start_datetime_objects, event_names)
        sorted_list = sorted(zipped_list, key=lambda pair: pair[0])
        past_dates_removed = [item for item in sorted_list if item[0] > datetime.now(timezone.utc)]
        dates = [item[0].strftime("%b %d, %Y") for item in past_dates_removed[0:5]]
        bands = [item[1] for item in past_dates_removed[0:5]]

        # TEST PRINT:
        # for band, date in zip(bands, dates):
        #     print(f"{date} -- {band}")

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_skylark():
    venue = "The Skylark Cafe"
    neighborhood = "West Seattle"
    url = "https://www.skylarkcafe.com/calendar"
    try:
        soup = get_soup(url)
        dates_unformatted = [date.text for date in soup.find_all("div", class_="date")]
        bands = [band.text.strip() for band in soup.find_all("div", class_="text-block-12")[0:5]]
        dates = [datetime.strptime(date, "%B %d, %Y %I:%M %p").strftime("%b %d, %Y")
                 for date in dates_unformatted[0:5]]
    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]
    return venue, url, neighborhood, bands, dates


def scrape_rendezvous():
    venue = "Rendezvous"
    website = "https://rendezvous.squarespace.com/events"
    neighborhood = "Belltown"

    current_month = datetime.now().month
    year_1 = datetime.now().year

    if current_month == 12:
        next_month = 1
        year_2 = year_1 + 1
    else:
        next_month = current_month + 1
        year_2 = year_1

    timestamp_current = f"{current_month:02d}-{year_1}"
    timestamp_next = f"{next_month:02d}-{year_2}"

    url_current = "https://rendezvous.squarespace.com/api/open/GetItemsByMonth?" \
                  f"month={timestamp_current}&" \
                  "collectionId=66df753bc3d7cc2eedfd6cfb&" \
                  "crumb=BeCoGhbDIcyIYWUwYTcwZDM5YTE2NTcxYThiMWJmNjZhY2VkYzI2"
    url_next = "https://rendezvous.squarespace.com/api/open/GetItemsByMonth?" \
               f"month={timestamp_next}&" \
               "collectionId=66df753bc3d7cc2eedfd6cfb&" \
               "crumb=BeCoGhbDIcyIYWUwYTcwZDM5YTE2NTcxYThiMWJmNjZhY2VkYzI2"
    try:
        data_current = request_json(url_current)
        data_next = request_json(url_next)
        data_current.reverse()
        data_next.reverse()
        data = data_current + data_next

        timestamps = [datetime.fromtimestamp(item["structuredContent"]["startDate"] / 1000) for item in data]
        dates_all = [date.strftime("%b %d, %Y") for date in timestamps]
        bands_all = [item["title"] for item in data]
        zipped_list = list(zip(dates_all, bands_all))
        future_event_pairs = [item for item in zipped_list
                              if datetime.strptime(item[0], "%b %d, %Y") > datetime.now()]
        dates = [pair[0] for pair in future_event_pairs[0:5]]
        bands = [pair[1] for pair in future_event_pairs[0:5]]

    except Exception:
        bands = ["No info - Click the venue name for info", "--", "--", "--", "--"]
        dates = ["--", "--", "--", "--", "--"]

    return venue, website, neighborhood, bands, dates


def scrape_triple_door():
    venue = "The Triple Door - Mainstage"
    website = "https://thetripledoor.net/mainstage-calendar"
    neighborhood = "Downtown"
    url = "https://thetripledoor.net/mainstage-calendar"

    soup = get_soup(url)
    act_tags = soup.find_all("span", class_="event-name alt-font")
    time_tags = soup.find_all("span", class_="time")
    date_tags = soup.find_all("span", class_="date")
    when_tags = soup.find_all("span", class_="event-when with-time")
    description_tags = soup.find_all("div", class_="event-description")
    # print(len(description_tags))
    acts = [act.text for act in act_tags]
    times = [time.text for time in time_tags]
    dates = [date.text for date in date_tags]

    print("hello")


def scrape_egans():
    pass


def scrape_wamu():
    pass


if __name__ == "__main__":
    print(scrape_crocodile())




