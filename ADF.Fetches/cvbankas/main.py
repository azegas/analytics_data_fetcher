from job_utils import (
    extract_details_of_many,
    save_cvbankas_jobs_locally,
    create_list_of_expiring_job_ads,
    extract_details_of_one,
)
from dotenv import load_dotenv
import os


def main():
    """Main function to fetch and save job ads."""

    load_dotenv()

    save_location = os.getenv("DATA_SAVE_LOCATION", "LOCAL").upper()
    fetch_specific = os.getenv("FETCH_SPECIFIC", "")

    if fetch_specific:
        expiring_job_ads_details = [extract_details_of_one(fetch_specific)]
    else:
        expiring_job_ads_list = create_list_of_expiring_job_ads()
        expiring_job_ads_details = extract_details_of_many(
            expiring_job_ads_list
        )

    if save_location == "LOCAL":
        save_cvbankas_jobs_locally(expiring_job_ads_details)
    else:
        pass


if __name__ == "__main__":
    main()
