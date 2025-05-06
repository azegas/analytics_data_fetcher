import requests
from extractors import (
    extract_articles,
    extract_id,
    extract_link,
    extract_title,
    extract_company,
    extract_salary,
    extract_when_posted,
    extract_city,
)
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path (for log_config)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_config import logger

pagesToFetch = 2  # how many pages to fetch?

load_dotenv()


def fetch_cvbankas_jobs():
    logger.info("Fetching CVBankas jobs...")
    jobs = []

    for page in range(1, pagesToFetch):

        url = f"https://en.cvbankas.lt/?page={page}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            articles = extract_articles(response)

            for job in articles:

                job_data = {
                    "job_id": extract_id(job),
                    "link": extract_link(job),
                    "title": extract_title(job),
                    "company": extract_company(job),
                    "salary": extract_salary(job),
                    "posted": extract_when_posted(job),
                    "city": extract_city(job),
                }
                jobs.append(job_data)

        except Exception as e:
            logger.error(f"Error fetching data for page {page}: {e}")

    logger.info(f"Fetched {len(jobs)} job listings")
    return jobs


def save_cvbankas_jobs(jobs):
    data_to_save = {
        "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "jobs": jobs,
    }

    file_path = os.path.join(os.getenv("BASE_DIR"), "data/cvbankas_ads.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        logger.info(f"Data saved to {file_path}")
    except IOError as e:
        logger.error(f"Failed to save data: {e}")


def main():
    jobs = fetch_cvbankas_jobs()
    save_cvbankas_jobs(jobs)


if __name__ == "__main__":
    main()
