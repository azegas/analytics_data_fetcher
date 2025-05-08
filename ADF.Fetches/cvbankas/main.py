from job_utils import (
    extract_details_of_many,
    save_job_ads,
    create_list_of_expiring_job_ads,
    extract_details_of_one,
)
from dotenv import load_dotenv
import os


def main():
    """Main function to fetch and save job ads."""

    load_dotenv()

    fetch_specific = os.getenv("FETCH_SPECIFIC", "")

    if fetch_specific:
        expiring_job_ads_details = [extract_details_of_one(fetch_specific)]
    else:
        expiring_job_ads_list = create_list_of_expiring_job_ads()
        expiring_job_ads_details = extract_details_of_many(
            expiring_job_ads_list
        )

    save_job_ads(expiring_job_ads_details)


if __name__ == "__main__":
    main()
