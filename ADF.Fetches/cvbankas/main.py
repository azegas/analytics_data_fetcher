from job_utils import fetch_cvbankas_jobs, save_cvbankas_jobs
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()

    # TODO find the total amount of pages
    # TODO start going from the last page, open only the ones that expire today (hours written instead of days)
    # TODO fetch all towns, if there are more
    # TODO fetch the views
    # TODO fetch the applications
    # TODO fetch rekvizitai info
    # TODO think about how to fetch and save requirements

    # Fetch jobs from CVBankas
    jobs = fetch_cvbankas_jobs(2)

    # Save the fetched jobs to a file
    save_cvbankas_jobs(jobs)


if __name__ == "__main__":
    main()
