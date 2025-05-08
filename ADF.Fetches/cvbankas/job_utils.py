from bs4 import BeautifulSoup
import requests
import json
import os
from datetime import datetime
from log_config import logger
from config import URL
from dotenv import load_dotenv
from extractor_article import ExtractorArticle
from extractor_job import ExtractorJob
import time
from parser import parse_job_details

extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()

try:
    fetch_limit = int(os.getenv("FETCH_LIMIT", 0))
except ValueError:
    fetch_limit = 0
    logger.warning(
        "FETCH_LIMIT in .env is not a valid integer. Defaulting to 0."
    )


def create_list_of_expiring_job_ads():
    expiring_ads = []
    pages_count = 0

    try:
        response = requests.get(URL)
        response.raise_for_status()

        last_page_number = extractor_article.extract_max_page_number(response)

        if last_page_number is None:
            logger.error("Could not determine the last page number.")
            return expiring_ads

        # Iterate from the last page to the first page
        for page in range(last_page_number, 0, -1):
            url = f"{URL}/?page={page}"

            response = requests.get(url)
            response.raise_for_status()

            articles = extractor_article.extract_articles(response)
            page_has_expiring_ads = False

            for job in articles:
                hours_left = extractor_article.extract_hours_left(job)
                if hours_left:
                    job_data = {
                        "link": extractor_article.extract_link(job),
                        "hours_left": hours_left,
                        "from_page": page,
                    }
                    expiring_ads.append(job_data)
                    page_has_expiring_ads = True

            # If no expiring ads were found on the page, break the loop
            if not page_has_expiring_ads:
                break

            pages_count += 1

        logger.debug(expiring_ads)

        logger.info(
            f"Fetched {len(expiring_ads)} expiring job ads from the last {pages_count} of {last_page_number} pages"
        )

        return expiring_ads

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return expiring_ads


def extract_details_of_one(job_link):

    try:
        response = requests.get(job_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        job_data = parse_job_details(job_link)

        return job_data

    except Exception as e:
        logger.error(f"Error fetching data for job ad {job_link}: {e}")
        return None


def extract_details_of_many(list_of_expiring_job_ads):
    total_ads = len(list_of_expiring_job_ads)
    fetched_count = 0
    jobs = []

    if fetch_limit > total_ads:
        ads_to_process = list_of_expiring_job_ads[:1]
        logger.warning(
            f"FETCH_LIMIT ({fetch_limit}) is greater than total ads ({total_ads}) "
            f"Fetching only 1 job ad instead."
        )
    elif 0 < fetch_limit <= total_ads:
        ads_to_process = list_of_expiring_job_ads[:fetch_limit]
        logger.info(
            f"Fetching {fetch_limit} job ads as requested in FETCH_LIMIT"
        )
    else:
        ads_to_process = list_of_expiring_job_ads
        logger.info(f"Fetching all {total_ads} job ads")

    logger.info("Fetch started...")

    time.sleep(5)

    for job_ad in ads_to_process:
        job_data = parse_job_details(job_ad["link"])
        if job_data:
            jobs.append(job_data)
            fetched_count += 1
            logger.info(
                f"Fetched {fetched_count}/{total_ads} | Remaining: {total_ads - fetched_count}"
            )

    logger.info(
        f"Finished fetching. Fetched {fetched_count} out of {total_ads}."
    )
    return jobs


def save_cvbankas_jobs_locally(jobs):
    data_to_save = {
        "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "jobs": jobs,
    }

    base_dir = os.getenv("BASE_DIR", os.getcwd())
    file_path = os.path.join(base_dir, "data/cvbankas_ads.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        logger.info(f"Data saved to {file_path}")
    except IOError as e:
        logger.error(f"Failed to save data: {e}")
