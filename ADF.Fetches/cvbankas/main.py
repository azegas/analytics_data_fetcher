import os
from dotenv import load_dotenv
from log_config import logger
from utils import process_expiring_job_ads
from db_stuff import (
    decide_upon_saving_location,
    save_job_ads,
    count_records_in_db,
    initialize_sqlite_db,
)
from extractors.extractor_other import extract_details_of_one


def main():
    """Main function to fetch and save job ads."""

    load_dotenv()

    fetch_specific = os.getenv("FETCH_SPECIFIC", "")
    saving_location = os.getenv("DATA_SAVE_LOCATION")

    decide_upon_saving_location(saving_location)
    initialize_sqlite_db()
    count_records_in_db()

    if fetch_specific:
        processed_jobs = [extract_details_of_one(fetch_specific)]
    else:
        processed_jobs = process_expiring_job_ads()

    save_job_ads(processed_jobs, saving_location)


if __name__ == "__main__":
    main()
