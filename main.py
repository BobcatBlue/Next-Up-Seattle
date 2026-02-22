from flask import Flask, render_template, make_response, send_from_directory, request, abort
import cronjob as cr
import csv
from google.cloud import storage
import io
from time import sleep
import ast


app = Flask(__name__)


"""
===================================
       DOWNLOAD AND RENDER
===================================
"""


def download_shows():
    file_name = "Show_Data.csv"
    bucket_name = "show_bucket"
    downloaded_shows = []
    show_dictionary = {}

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    returned_csv_content = blob.download_as_text()
    # print(returned_csv_content)

    with io.StringIO(returned_csv_content) as file:
        reader = csv.reader(file)
        for row in reader:
            downloaded_shows.append(row)

    for item in downloaded_shows:
        bands_string = item[3]
        dates_string = item[4]
        bands_list = ast.literal_eval(bands_string)
        dates_list = ast.literal_eval(dates_string)
        item[3] = bands_list
        item[4] = dates_list
        show_dictionary[item[0]] = item[1:]

    return show_dictionary


@app.route("/")
def new_index():
    dictionary = download_shows()

    response = make_response(render_template("index.html", dictionary=dictionary))
    response.headers["Connection"] = "close"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    return response


@app.route("/Contact_Us")
def contact_us():
    response = make_response(render_template("Contact Us.html"))
    return response


@app.route("/About")
def about_us():
    response = make_response(render_template("About.html"))
    return response


"""
=================================
       SCRAPE AND UPLOAD
================================
"""


@app.route("/cron/daily")
def cron_daily():
    if request.headers.get("X-Appengine-Cron") != "true":
        abort(403)

    run_update_job()
    return "Update Successful"


@app.route("/admin/run-update")
def admin_run_update():
    if app.debug is not True:
        abort(403)

    run_update_job()
    return "Manually triggered ratta-tat-tat"


def run_update_job():
    print("Updating CSV...")

    upload_shows = []
    file_name = "Show_Data.csv"
    bucket_name = "show_bucket"

    upload_shows.extend([
        cr.scrape_central(),
        cr.scrape_babayaga(),
        cr.scrape_el_corazon(),
        cr.scrape_funhouse(),
        cr.scrape_nuemos(),
        cr.scrape_showbox_presents()[0],
        cr.scrape_showbox_presents()[1],
        cr.scrape_nectar(),
        cr.scrape_hidden_hall(),
        cr.scrape_substation(),
        cr.scrape_neptune(),
        cr.scrape_crocodile(),
        cr.scrape_tractor_tavern(),
        cr.scrape_sunset_tavern(),
        cr.scrape_conor_byrne(),
        cr.scrape_seamonster(),
        cr.scrape_bluemoon(),
        cr.scrape_royal_room()
    ])

    fn_client = storage.Client()
    fn_bucket = fn_client.bucket(bucket_name)
    fn_blob = fn_bucket.blob(file_name)

    # Write upload_shows to a variable which acts like a CSV file
    with io.StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(upload_shows)
        csv_content = csvfile.getvalue()

    # Upload the csv-like variable to an actual CSV file on the server
    fn_blob.upload_from_string(csv_content, content_type="text/csv")
    sleep(1.5)

    # Print out the information in a nice format
    show_dictionary = {}
    for item in upload_shows:
        show_dictionary[item[0]] = item[1:]

    return "The CSV has been successfully updated"


if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
    # app.run(debug=True, port=5001, use_reloader=False, host="0.0.0.0")


