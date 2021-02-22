import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime as dt
from datetime import timedelta
import os
import difflib
import click
# from email_handler import EmailHandler, create_email

TODAY = dt.now().date()
YESTERDAY = TODAY - timedelta(days=1)
TODAY_UNDERSCORE = str(TODAY).replace("-", "_")
YESTERDAY_UNDERSCORE = str(YESTERDAY).replace("-", "_")


def get_last_update_date():
    covid_update = "https://www.immigration.govt.nz/site-messages.js"
    r = requests.get(covid_update)

    if r.status_code != 200:
        raise ConnectionError(f"HTTP status code {r.status_code}: {r.reason}")

    alert_data = json.loads(r.text.split("inz.siteWideAlerts.data=")[1])

    messages = [msg for e in alert_data['envelopes'] for msg in e['messages'] ]

    for msg in messages:
        if msg.get('title') == "COVID-19":
            date = msg.get('date')

            return dt.strptime(date, "%A %d %B %Y / %I:%M %p NZDT").date()


def get_inz_update(url):

    r = requests.get(url).content
    soup = BeautifulSoup(r, "html.parser")

    return soup.find("div", class_="content").text


def check_content_update(root_folder, file, word_wrap=110):

    yesterday_file = os.path.join(root_folder, YESTERDAY_UNDERSCORE, file)

    if not os.path.exists(yesterday_file):
        print(f"No {file} file to compare to. Skipping.")
        return None

    with open(yesterday_file) as inf:
        yesterday_content = inf.readlines()

    with open(os.path.join(root_folder, TODAY_UNDERSCORE, file)) as inf:
        today_content = inf.readlines()

    if not yesterday_content == today_content:
        diff_file = difflib.HtmlDiff(wrapcolumn=word_wrap).make_file(
            fromlines=yesterday_content,
            tolines=today_content,
            fromdesc=YESTERDAY_UNDERSCORE,
            todesc=TODAY_UNDERSCORE
        )
        diff_file_name = f"diff_{file}.html"
        diff_file_path = os.path.join(root_folder, TODAY_UNDERSCORE, diff_file_name)
        with open(diff_file_path, "w") as outf:
            outf.write(diff_file)
            print(f"CONTENT CHANGED SINCE YESTERDAY, DIFF FILE AVAILABLE AT: {diff_file_path}")
        return diff_file
    else:
        print(f"No change to {file}")
        return None


@click.command()
@click.option("--inz-info-dir", required=True, help="Directory to save and load info from INZ website")
# @click.option("--sender-email", envvar="SENDER_EMAIL", required=False, help="Email address, sender of the notification email")
# @click.option("--password-email", envvar="PASSWORD_EMAIL", required=False, help="Password for the mailbox sending email")
# @click.option("--receiver-email", envvar="RECEIVER_EMAIL", required=False, help="Email address, receiver of the notification email")
def main(**options):

    updates = {}

    inz_info_dir = options.get("inz_info_dir")
    if not os.path.exists(inz_info_dir):
        raise NotADirectoryError(f"The directory {inz_info_dir} doesn't exists.")

    today_dir = os.path.join(inz_info_dir, TODAY_UNDERSCORE)
    os.makedirs(today_dir, exist_ok=True)

    # Check site wide banner for a new important update
    last_update = get_last_update_date()
    print(last_update)

    if last_update >= TODAY:
        print("NEW BANNER ALERT")
        updates['banner'] = f"Banner was updated on {last_update}"
    else:
        print("No new banner update")
        updates['banner'] = None

    url_to_check = {
        "migrant_info": "https://www.immigration.govt.nz/about-us/covid-19/outside-of-new-zealand/migrant-information",
        "entry_reason": "https://www.immigration.govt.nz/about-us/covid-19/border-closures-and-exceptions/critical-purpose-reasons-you-can-travel-to-new-zealand",
        "entry_request": "https://www.immigration.govt.nz/about-us/covid-19/border-closures-and-exceptions/how-to-request-to-travel",
        "entry_requirement": "https://www.immigration.govt.nz/about-us/covid-19/border-closures-and-exceptions/border-entry-requirements"
    }

    for update_type, url in url_to_check.items():
        update = get_inz_update(url)
        diff_file = os.path.join(today_dir, update_type)
        with open(diff_file, "w") as outf:
            outf.write(update)
        diff = check_content_update(root_folder=inz_info_dir, file=update_type)
        updates[update_type] = diff

    # if options.get('sender_email') and any(updates.values()):
    #     sender = login=options.get('sender_email')
    #     notifier = EmailHandler(sender, password=options.get('password_email'))
    #
    #     for item, update in updates.items():
    #         if update:
    #             email = create_email(
    #                 sender_email=sender,
    #                 receiver_email=options.get("receiver_email"),
    #                 subject=f"INZ website updated - {item}",
    #                 text=update
    #             )
    #             notifier.send_email(email)


if __name__ == "__main__":
    main()
