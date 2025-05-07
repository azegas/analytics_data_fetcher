from job_utils import (
    extract_details,
    save_cvbankas_jobs_locally,
    create_list_of_expiring_job_ads,
)
from dotenv import load_dotenv
import os


def main():
    """Main function to fetch and save job ads."""

    load_dotenv()

    save_location = os.getenv("DATA_SAVE_LOCATION", "LOCAL").upper()

    expiring_job_ads_list = create_list_of_expiring_job_ads()

    expiring_job_ads_details = extract_details(expiring_job_ads_list)

    if save_location == "LOCAL":
        save_cvbankas_jobs_locally(expiring_job_ads_details)
    else:
        pass


if __name__ == "__main__":
    main()
