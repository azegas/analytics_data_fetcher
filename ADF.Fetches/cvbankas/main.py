import os
from dotenv import load_dotenv
from log_config import logger
from utils import decide_if_fetching_many_or_one
from db_stuff import (
    decide_upon_saving_location,
    save_job_ads,
    count_records_in_db,
    initialize_sqlite_db,
)


def main():
    """Main function to fetch and save job ads."""

    load_dotenv()

    fetch_specific = os.getenv("FETCH_SPECIFIC", "")
    saving_location = os.getenv("DATA_SAVE_LOCATION")

    decide_upon_saving_location(saving_location)
    initialize_sqlite_db()
    count_records_in_db()

    expiring_job_ads_details = decide_if_fetching_many_or_one(fetch_specific)

    save_job_ads(expiring_job_ads_details, saving_location)


if __name__ == "__main__":
    main()
