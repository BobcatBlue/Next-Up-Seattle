from flask import Flask, render_template, make_response, send_from_directory
import cronjob as cr
import csv
from google.cloud import storage
import io
from time import sleep


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
        bands_list = eval(bands_string)
        dates_list = eval(dates_string)
        item[3] = bands_list
        item[4] = dates_list
        show_dictionary[item[0]] = item[1:]

    return show_dictionary


@app.route("/")
def new_index():
    dictionary = download_shows()

    response = make_response(render_template("index.html", dictionary=dictionary))
    response.headers["Connection"] = "close"
    response.headers["Cache-Control"] = "no-store, no-cash, must-revalidate, max-age=0"
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


@app.route("/cron")
def update_csv():
    print("Updating CSV...")
    upload_shows = []
    file_name = "Show_Data.csv"
    bucket_name = "show_bucket"

    central_saloon = cr.scrape_central()
    baba_yaga = cr.scrape_babayaga()
    el_corazon = cr.scrape_el_corazon()
    funhouse = cr.scrape_funhouse()
    nuemos = cr.scrape_nuemos()
    showboxes = cr.scrape_showbox_presents()
    nectar = cr.scrape_nectar()
    hidden_hall = cr.scrape_hidden_hall()
    crocodile = cr.scrape_crocodile()
    madame_lous = cr.scrape_madame_lous()
    tractor_tavern = cr.scrape_tractor_tavern()
    conor_byrne = cr.scrape_conor_byrne()
    seamonster = cr.scrape_seamonster()

    upload_shows.append(central_saloon)
    upload_shows.append(baba_yaga)
    upload_shows.append(el_corazon)
    upload_shows.append(funhouse)
    upload_shows.append(nuemos)
    upload_shows.append(showboxes[0])
    upload_shows.append(showboxes[1])
    upload_shows.append(nectar)
    upload_shows.append(hidden_hall)
    upload_shows.append(crocodile)
    upload_shows.append(madame_lous)
    upload_shows.append(tractor_tavern)
    upload_shows.append(conor_byrne)
    upload_shows.append(seamonster)

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

    return "The CSV has been successfully update"


if __name__ == "__main__":
    # app.run(debug=True, port=5001, use_reloader=False)
    app.run(debug=True, port=5001, use_reloader=False, host="0.0.0.0")


