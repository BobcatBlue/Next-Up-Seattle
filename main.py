from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask, render_template, make_response, send_from_directory, request, abort
import cronjob as cr
import csv
from google.cloud import storage
import io
from time import sleep
import ast
import pprint


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
    # pprint(returned_csv_content)

    with io.StringIO(returned_csv_content) as file:
        reader = csv.reader(file)
        for row in reader:
            downloaded_shows.append(row)


    """============TEST PRINTS============"""
    # pprint.pp(downloaded_shows)
    # for item in downloaded_shows[0]:
    #     print(item)
    """+=================================="""


    for item in downloaded_shows:
        # print(item)
        """
                                        FOR THE REWORK
        -------------------------------------------------------------------------------
        This is where date/time info will be converted back into a datetime object
        from the ISO-string that is going to be stored in the CSV file.
        
        The objects will be converted into the ISO-strings in their individual modules
        in cron.py, before being sent over here to main.py to be uploaded to the cloud.
        
        First, the data will be extracted from CSV into the downloaded_shows list, just 
        like it is right now, but now with this new additional string data.  Then we'll
        conver that into a list, just like bands_list and dates_list are created (see 
        below).  Then iterate through that list and convert each item back into a 
        datetime object.
        
        Easy Peasy
        -------------------------------------------------------------------------------
        """

        bands_string = item[3]
        dates_string = item[4]
        bands_list = ast.literal_eval(bands_string)
        dates_list = ast.literal_eval(dates_string)
        item[3] = bands_list
        item[4] = dates_list

        if 0 <= 6 < len(item):
            ticket_urls = ast.literal_eval(item[6])
            print(type(ticket_urls))
            item[6] = ticket_urls



        """The following if/else statement is only necessary while all the scraping
        modules have NOT been updated to include datetime objects"""

        if 5 < len(item):
            iso_string = item[5]
            iso_list = ast.literal_eval(iso_string)
            # dt_list = [datetime.fromisoformat(iso) for iso in iso_list]

            dt_list = []
            for iso in iso_list:
                if iso == "--":
                    dt_list.append(item)
                else:
                    dt_list.append(datetime.fromisoformat(iso))
            item[5] = dt_list
            # for list_item in item[5]:
            #     print(list_item.strftime("%a %d %#I:%M %p"))
        else:
            pass


        show_dictionary[item[0]] = item[1:]

    """============TEST PRINTS============"""
    # pprint.pp(downloaded_shows)
    # print(type(show_dictionary))
    # print(show_dictionary)
    pprint.pp(show_dictionary)
    """++++++++++++======================="""


    return show_dictionary


@app.route("/")
def index():
    dictionary = download_shows()
    # pprint.pp(dictionary)

    response = make_response(render_template("index.html", dictionary=dictionary))
    response.headers["Connection"] = "close"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    return response


@app.route("/home")
def home():
    dictionary = download_shows()
    response = make_response(render_template("home.html",
                                             dictionary=dictionary,
                                             datetime=datetime))
    response.headers["Connection"] = "close"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    return response


@app.route("/index2")
def index2():
    dictionary = download_shows()
    # pprint.pp(dictionary)

    response = make_response(render_template("new_index.html",
                                             dictionary=dictionary,
                                             datetime=datetime))
    response.headers["Connection"] = "close"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    return response


@app.route("/Contact_Us")
def contact_us():
    response = make_response(render_template("Contact Us.html"))
    return response


@app.route("/Contact")
def new_contact_us():
    response = make_response(render_template("new_contact_us.html"))
    return response


@app.route("/About")
def about_us():
    response = make_response(render_template("About.html"))
    return response


@app.route("/AboutUs")
def new_about_us():
    response = make_response(render_template("new_about_us.html"))
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
    # print("Updating CSV...")

    upload_shows = []
    file_name = "Show_Data.csv"
    bucket_name = "show_bucket"

    upload_shows.extend([
        cr.scrape_central(),
        cr.scrape_babayaga(),
        cr.scrape_el_corazon(),
        cr.scrape_funhouse(),
        cr.scrape_neumos(),
        cr.scrape_barboza(),
        cr.scrape_showbox_presents()[0],
        cr.scrape_showbox_presents()[1],
        cr.scrape_nectar(),
        cr.scrape_hidden_hall(),
        cr.scrape_substation(),
        # cr.scrape_neptune(),
        cr.scrape_crocodile(),
        cr.scrape_rendezvous(),
        cr.scrape_tractor_tavern(),
        cr.scrape_sunset_tavern(),
        cr.scrape_conor_byrne(),
        cr.scrape_seamonster(),
        cr.scrape_bluemoon(),
        cr.scrape_royal_room(),
        cr.scrape_skylark()
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
    # app.run(debug=True, port=5001, use_reloader=False)
    app.run(debug=True, port=5001, use_reloader=False, host="0.0.0.0")


