from flask import Flask, render_template, make_response
import cronjob
from datetime import datetime
import pandas as pd
from time import sleep
import csv
from google.cloud import storage
import io


app = Flask(__name__)

SHOWS = []
URLS = []

df_URL = pd.read_csv("URLs.csv")
url_list = df_URL.values.tolist()
for item in url_list:
    URLS.append(item[0])


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
    global URLS
    shows = download_shows()
    response = make_response(render_template("index.html", shows=shows, urls=URLS))
    response.headers["Cache-Control"] = "no-store"
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

    # Scrape, motherfucker, SCRAPE!
    central = cronjob.scrape_central()
    corazon = cronjob.scrape_el_corazon()
    funhouse = cronjob.scrape_funhouse()
    nectar = cronjob.scrape_nectar()
    highdive = cronjob.scrape_highdive()
    showboxes = cronjob.scrape_showbox_presents()

    SHOWS.append(["Central Saloon", central[0], central[1]])
    SHOWS.append(["El Corazon", corazon[0], corazon[1]])
    SHOWS.append(["Funhouse", funhouse[0], funhouse[1]])
    SHOWS.append(["Nectar Lounge", nectar[0], nectar[1]])
    SHOWS.append(["High Dive Seattle", highdive[0], highdive[1]])
    SHOWS.append(showboxes[0])
    SHOWS.append(showboxes[1])

    # Pull all of the show data from TM venues, append them to SHOWS
    # This call_shows() is defined locally and is not the same as the one in cronjob.py module
    call_shows()
    print(SHOWS)

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



if __name__ == "__main__":
    # app.run(debug=True, port=5001, use_reloader=False, host="0.0.0.0")
    app.run(debug=True, port=5001, use_reloader=False)


