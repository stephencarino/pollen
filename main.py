import time
import datetime
import requests
import pandas as pd
import csv
import os
import shutil

BASE_URL = "https://xapps.ncdenr.org/aq/ambient/Pollen.jsp"

POLLEN_TYPE_FNAME = "./data/pollen-type.csv"
POLLEN_TOTAL_FNAME = "./data/pollen-total.csv"


def init_data_files():
    """
    Delete existing files and folders
    Creates a new folder
    """
    # remove data folder
    try:
        shutil.rmtree("./data")
    except Exception as e:
        print(e)

    # create data folder
    os.makedirs("./data")

    # create files and header data
    with open(POLLEN_TYPE_FNAME, "w") as f:
        f.write("Type|Number of Grains|Severity|Pollen Count (Grains/m^3)|Date\n")

    with open(POLLEN_TOTAL_FNAME, "w") as f:
        f.write("Total (Grains/m^3)|Comments|Date\n")


def get_today() -> str:
    """
    Return today's date as a string
    """
    return datetime.datetime.today().strftime("%m/%d/%Y")


def init_db(startDate: str, endDate: str):
    """
    Create new CSV files
    """

    init_data_files()

    # numDays = 365 * 15  # get 15 years of data

    dateCurrent = datetime.datetime.strptime(startDate, "%m/%d/%Y")
    dateEnd = datetime.datetime.strptime(endDate, "%m/%d/%Y")
    delta = datetime.timedelta(days=1)

    while dateCurrent <= dateEnd:
        get_pollen_data(dateCurrent.strftime("%m/%d/%Y"))
        dateCurrent += delta


def get_pollen_data(dateStr):
    """
    Get data from the website
    """
    # dateStr = datetime.datetime.today().strftime("%m/%d/%Y")

    try:
        r = requests.get(f"{BASE_URL}?date={dateStr}")
    except Exception as e:
        print(e)
        print(f"Status code: {r.status_code}")
        print(f"No data for {dateStr}.")
        pass

    try:
        data = pd.read_html(r.content)[0]
        # segregate total pollen count and comments
        data2 = pd.DataFrame(
            [
                {
                    "Total (grains/m3)": data.iloc[3, 0]
                    .partition("Total Pollen Count for this Reporting Period: ")[2]
                    .partition(" grains/m3.")[0],
                    "Comments": data.iloc[4, 0].partition(": ")[2].partition(".")[0],
                    "Date": dateStr,
                }
            ]
        )

        data = data.loc[0:2]  # only grab the first three rows
        data["Date"] = data.apply(lambda row: dateStr, axis=1)

        data.to_csv(
            POLLEN_TYPE_FNAME,
            header=None,
            mode="a",
            index=False,
            quoting=csv.QUOTE_NONE,
            sep="|",
        )
        data2.to_csv(
            POLLEN_TOTAL_FNAME,
            header=None,
            mode="a",
            index=False,
            quoting=csv.QUOTE_MINIMAL,
            sep="|",
        )
    except Exception as e:
        print(e)
        print(f"No data for {dateStr}")


# init_db()
# get_pollen_data("4/28/2023")
# print(get_today())
