from job_utils import (
    extract_details,
    save_cvbankas_jobs,
    create_list_of_expiring_job_ads,
)
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()

    # TODO think about how to fetch and save requirements
    # TODO static methods - figure out why they are wrong
    # TODO debug logs - be able to change he debug level from the .env or from the config
    # TODO logs should logs stuff about the actualy method not about the wrapper method (extract_category if the error is here and not extract_details for example)

    expiring_job_ads_list = create_list_of_expiring_job_ads()

    # Fetch jobs from CVBankas
    expiring_job_ads_details = extract_details(expiring_job_ads_list)

    # Save the fetched jobs to a file
    save_cvbankas_jobs(expiring_job_ads_details)


if __name__ == "__main__":
    main()
