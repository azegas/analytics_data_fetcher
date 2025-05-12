import os
from dotenv import load_dotenv
from other_stuff.log_config import logger
from other_stuff.utils import process_expiring_job_ads
from other_stuff.db_stuff import (
    decide_upon_saving_location,
    save_job_ads,
    count_records_in_db,
    initialize_sqlite_db,
)
from extractors.extractor_other import extract_details_of_one
from other_stuff.send_email import send_email


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

    total_records_in_db = count_records_in_db()

    email_subject = (
        f"ADF: new: {len(processed_jobs)}, total: {total_records_in_db}"
    )
    email_body = ""

    send_email(email_subject, email_body)

    logger.info("DONE. See you later.")


if __name__ == "__main__":
    main()
