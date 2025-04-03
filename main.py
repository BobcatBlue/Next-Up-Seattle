from flask import Flask, render_template, make_response, send_from_directory
import cronjob
from datetime import datetime
import pandas as pd
from time import sleep
import csv
from google.cloud import storage
import io


app = Flask(__name__)

SHOWS = []
SITES_AND_HOODS = pd.read_csv("URLs.csv")
VENUE_INFO = SITES_AND_HOODS.values.tolist()

# Reference your bucket and blob (file)
BUCKET_NAME = "show_bucket"
FILE_NAME = "Show_Data.csv"


def download_shows():
    global BUCKET_NAME
    global FILE_NAME
    shows = []
    # Initialize the cloud storage client:
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILE_NAME)
    # Read the CSV file from GCS and store it in SHOWS:
    csv_content = blob.download_as_text()

    with io.StringIO(csv_content) as file:
        reader = csv.reader(file)
        for row in reader:
            shows.append(row)

    return shows


def call_shows():
    df = pd.read_csv("Listed_Venues.csv")
    print("Ring ring!!!  I'm inside call_shows(), calling the API")
    for index, row in df.iterrows():
        venue, band, date = cronjob.get_shows(row["Venue Name"], row["vID"])
        if date == "No info":
            SHOWS.append([venue, "No Info", "No Info"])
        else:
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
            SHOWS.append([venue, band, date])
        sleep(0.09)


@app.route("/")
def index():
    global VENUE_INFO
    shows = download_shows()

    dictionary = {}
    counter = 0
    for item in shows:
        dictionary[item[0]] = item[1:]   # Assign the venue name as a dictionary key
        dictionary[item[0]].insert(0, VENUE_INFO[counter][0])   # Add venue's website to the list
        dictionary[item[0]].insert(1, VENUE_INFO[counter][1])   # Add venue's neighborhood to list
        counter += 1

    print("This is just the index")
    print(dictionary)

    response = make_response(render_template("index.html", dictionary=dictionary))
    # response.headers["Cache-Control"] = "no-store"
    response.headers["Connection"] = "close"
    response.headers["Cache-Control"] = "no-store, no-cash, must-revalidate, max-age=0"
    response.headers["Expires"] = '0'
    return response


@app.route("/Contact_Us")
def contact_us():
    response = make_response(render_template("Contact Us.html"))
    return response


@app.route("/About_Us")
def about_us():
    response = make_response(render_template("About.html"))
    return response


@app.route("/cron")
def update_csv():
    print("I am here in UPDATE CSV")
    global SHOWS
    global BUCKET_NAME
    global FILE_NAME
    SHOWS = []

    # Scrape...SCRAAAAAAAAPE!
    central = cronjob.scrape_central()
    baba_yaga = cronjob.scrape_babayaga()
    corazon = cronjob.scrape_el_corazon()
    funhouse = cronjob.scrape_funhouse()
    nectar = cronjob.scrape_nectar()
    highdive = cronjob.scrape_highdive()
    conor_byrne = cronjob.scrape_conor_byrne()
    tractor = cronjob.scrape_tractor_tavern()
    egans = cronjob.scrape_egans()
    seamonster = cronjob.scrape_seamonster()
    crocodile = cronjob.scrape_crocodile()
    madame_lous = cronjob.scrape_madame_lous()
    nuemos = cronjob.scrape_nuemos()
    showboxes = cronjob.scrape_showbox_presents()
    # wamu = cronjob.scrape_wamu()
    # climate_pledge = cronjob.scrape_climate_pledge()


    SHOWS.append(["Central Saloon", central[0], central[1]])
    SHOWS.append(["Baba Yaga", baba_yaga[0], baba_yaga[1]])
    SHOWS.append(["El Corazon", corazon[0], corazon[1]])
    SHOWS.append(["Funhouse", funhouse[0], funhouse[1]])
    SHOWS.append(["Nectar Lounge", nectar[0], nectar[1]])
    SHOWS.append(["High Dive Seattle", highdive[0], highdive[1]])
    SHOWS.append(["Conor Byrne", conor_byrne[0], conor_byrne[1]])
    SHOWS.append(["Tractor Tavern", tractor[0], tractor[1]])
    SHOWS.append(["Egan's Ballard Jam House", egans[0], egans[1]])
    SHOWS.append(["Sea Monster Lounge", seamonster[0], seamonster[1]])
    SHOWS.append(["The Crocodile", crocodile[0], crocodile[1]])
    SHOWS.append(["Madame Lou's", madame_lous[0], madame_lous[1]])
    SHOWS.append(["Nuemos", nuemos[0], nuemos[1]])
    SHOWS.append(showboxes[0])
    SHOWS.append(showboxes[1])
    call_shows()

    # Ideally wanted to use these scraping modules, but the websites are problematic
    # SHOWS.append(["WAMU Theater", wamu[0], wamu[1]])
    # SHOWS.append(["Climate Pledge Arena", climate_pledge[0], climate_pledge[1]])

    # "fn" stands for "function"
    fn_client = storage.Client()
    fn_bucket = fn_client.bucket(BUCKET_NAME)
    fn_blob = fn_bucket.blob(FILE_NAME)

    # Write SHOWS to the csv file hosted on Google Cloud
    with io.StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(SHOWS)
        csv_content = csvfile.getvalue()

    fn_blob.upload_from_string(csv_content, content_type="text/csv")

    sleep(1.5)

    return "CSV update was successful.  I think.  I mean, it didn't crash, so that's good.  " \
           "Baby steps...baby steps"


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")


if __name__ == "__main__":
    # app.run(debug=True, port=5001, use_reloader=False, host="0.0.0.0")
    app.run(debug=True, port=5001, use_reloader=False)


