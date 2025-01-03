import argparse
import logging
from datetime import datetime, timedelta
from time import sleep

import chime
import requests

chime.theme("zelda")
logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def get_parser():
    parser = argparse.ArgumentParser(description="Checking cbp availability")

    parser.add_argument(
        "-s",
        "--start",
        type=str,
        default="",
        help="Start date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "-e",
        "--end",
        type=str,
        default="",
        help="End date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default="15",
        help="The interval of checking the availability in seconds",
    )

    parser.add_argument(
        "-l",
        "--location",
        type=int,
        default="5020",  # Blaine, WA
        help="The location id",
    )

    return parser


def get_availability(start_timestamp, end_timestamp, location_id, args):

    TIMESPAN_URL = "https://ttp.cbp.dhs.gov/schedulerapi/locations/{}/slots?startTimestamp={}&endTimestamp={}"

    start_timestamp.replace(microsecond=0)
    end_timestamp.replace(microsecond=0)
    found_available = False
    i = 0
    logging.info("Retrieving availability from location...")

    while found_available is not True:
        try:
            url = TIMESPAN_URL.format(
                location_id, start_timestamp.isoformat(), end_timestamp.isoformat()
            )
            slots = requests.get(url).json()
            available_slots = [slot["timestamp"] for slot in slots if slot["active"]]
            logging.info(
                "{} - {}: {} slots available".format(
                    start_timestamp, end_timestamp, len(available_slots)
                )
            )
            if available_slots:
                chime.info()
                logging.info(available_slots)
                break

        except:
            logging.warning("Error when fetching the api")

        logging.info("Sleep for " + str(args.interval) + " sec")
        sleep(args.interval)


def main():
    parser = get_parser()
    args = parser.parse_args()

    # get start time and end time for quick sanity check
    if args.start == "":
        start_time = (datetime.today() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        start_time = datetime.strptime(args.start, "%Y-%m-%d")

    if args.end == "":
        # default end time is 7 day after start time
        end_time = start_time + timedelta(days=7)
    else:
        end_time = datetime.strptime(args.end, "%Y-%m-%d")

    if start_time > end_time:
        logging.error("Start date must be before end date")
        exit(1)

    logging.info("Checking availability from {} to {}...".format(start_time, end_time))

    get_availability(start_time, end_time, args.location, args)


if __name__ == "__main__":
    main()
