from job_utils import (
    fetch_details_of_each_job,
    save_cvbankas_jobs,
    create_list_of_expiring_job_ads,
)
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()

    # TODO fetch all towns, if there are more
    # TODO fetch the views
    # TODO fetch the applications
    # TODO fetch rekvizitai info
    # TODO think about how to fetch and save requirements

    expiring_job_ads = create_list_of_expiring_job_ads()

    # Fetch jobs from CVBankas
    jobs = fetch_details_of_each_job(expiring_job_ads)

    # Save the fetched jobs to a file
    save_cvbankas_jobs(jobs)


if __name__ == "__main__":
    main()
