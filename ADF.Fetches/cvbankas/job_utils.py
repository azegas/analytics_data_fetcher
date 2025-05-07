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
    extract_category_from_detail_page,
    extract_max_page_number,
    extract_hours_left,
)
import json
import os
from datetime import datetime
from log_config import logger
from config import URL

# start going from the last page, if article has "xx hours left"

# then take it's link and hours left, put into a list
# if the page does not have those - break


def create_list_of_expiring_job_ads():
    expiring_ads = []
    pages_count = 0

    try:
        response = requests.get(URL)
        response.raise_for_status()

        last_page_number = extract_max_page_number(response)

        if last_page_number is None:
            logger.error("Could not determine the last page number.")
            return expiring_ads

        # Iterate from the last page to the first page
        for page in range(last_page_number, 0, -1):
            url = f"{URL}/?page={page}"
            response = requests.get(url)
            response.raise_for_status()

            articles = extract_articles(response)
            page_has_expiring_ads = False

            for job in articles:
                hours_left = extract_hours_left(job)
                if hours_left:
                    job_data = {
                        "link": extract_link(job),
                        "hours_left": hours_left,
                        "from_page": page,
                    }
                    expiring_ads.append(job_data)
                    page_has_expiring_ads = True

            # If no expiring ads were found on the page, break the loop
            if not page_has_expiring_ads:
                break

            pages_count += 1

        logger.info(expiring_ads)

        logger.info(
            f"Fetched {len(expiring_ads)} expiring job ads from the last {pages_count} of {last_page_number} pages"
        )

        return expiring_ads

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return expiring_ads


# duok jam ne pages to fetch, BET TIK array of articles to make the calls for
def fetch_cvbankas_jobs(pagesToFetch):
    logger.info("Fetching CVBankas jobs...")
    jobs = []

    for page in range(1, pagesToFetch):
        url = f"{URL}/?page={page}"

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
                    "category": extract_category_from_detail_page(
                        extract_link(job)
                    ),
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
