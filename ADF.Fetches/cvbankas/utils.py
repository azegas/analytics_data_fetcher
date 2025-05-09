import requests
from config import URL
from log_config import logger
from dotenv import load_dotenv

from extractors.extractor_other import (
    extract_details_of_many,
    extract_details_of_one,
)

from extractors.extractor_article import ExtractorArticle
from extractors.extractor_job import ExtractorJob
from db_stuff import get_existing_job_ids_from_db
from utils2 import extract_after_last_slash


extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()


def decide_if_fetching_many_or_one(fetch_specific):
    if fetch_specific:
        expiring_job_ads_details = [extract_details_of_one(fetch_specific)]
    else:
        expiring_job_ads_list = create_list_of_expiring_job_ads()

        if not expiring_job_ads_list:
            logger.info("No expiring job ads found. Stopping the script.")
            expiring_job_ads_details = []
            return

        expiring_job_ads_details = extract_details_of_many(
            expiring_job_ads_list
        )

    return expiring_job_ads_details


def create_list_of_expiring_job_ads():
    expiring_ads = []
    pages_count = 0
    repeating_jobs = 0
    repeating_jobs_present = False

    existing_job_ids = get_existing_job_ids_from_db()

    try:
        response = requests.get(URL)
        response.raise_for_status()

        last_page_number = extractor_article.extract_max_page_number(response)

        for current_page_number in range(last_page_number, 0, -1):
            new_ads, page_has_expiring_ads, page_has_repeats, page_repeats = (
                process_single_page(current_page_number, existing_job_ids)
            )

            if not page_has_expiring_ads:
                logger.info(
                    f"No expiring ads found on page {current_page_number}. Breaking loop. Stopping the search for expiring job ads."
                )
                break

            expiring_ads.extend(new_ads)
            pages_count += 1
            repeating_jobs += page_repeats
            repeating_jobs_present = repeating_jobs_present or page_has_repeats

        if repeating_jobs_present:
            logger.info(
                f"Skipped {repeating_jobs} jobs that already exist in the database."
            )
        else:
            logger.info("No repeating jobs found in any of the pages.")

        logger.debug(expiring_ads)
        logger.info(
            f"Fetched {len(expiring_ads)} NEW expiring job ads from the last {pages_count} of {last_page_number} pages"
        )

        return expiring_ads

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return expiring_ads


def process_single_page(page, existing_job_ids):
    url = f"{URL}/?page={page}"
    logger.info(f"Processing page: {page}")

    response = requests.get(url)
    response.raise_for_status()

    articles = extractor_article.extract_articles(response)
    logger.info(f"Number of articles on page {page}: {len(articles)}")

    new_ads = []
    page_has_expiring_ads = False
    repeating_jobs_present = False
    repeating_jobs = 0

    for job in articles:
        hours_left = extractor_article.extract_hours_left(job)
        if hours_left:
            job_id = extract_after_last_slash(
                extractor_article.extract_link(job)
            )
            logger.info(f"Checking job ID: {job_id}")
            if job_id not in existing_job_ids:
                job_data = {
                    "job_id": job_id,
                    "job_link": extractor_article.extract_link(job),
                    "hours_left": hours_left,
                    "from_page": page,
                }
                new_ads.append(job_data)
                page_has_expiring_ads = True
            else:
                logger.info(
                    f"Job ID {job_id} already exists in the database. Skipping."
                )
                repeating_jobs_present = True
                repeating_jobs += 1

    return (
        new_ads,
        page_has_expiring_ads,
        repeating_jobs_present,
        repeating_jobs,
    )
