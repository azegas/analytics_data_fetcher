import os
import time

import requests
from bs4 import BeautifulSoup
from config import URL
from dotenv import load_dotenv
from extractors.extractor_article import ExtractorArticle
from extractors.extractor_job import ExtractorJob
from extractors.parser import parse_job_details
from log_config import logger

extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()


def extract_details_of_one(job_link):
    logger.info(f"Fetching a single specific job ad from {job_link}")

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

    # TODO figure out why fetch limit is not working
    try:
        fetch_limit = int(os.getenv("FETCH_LIMIT", 0))
        logger.info(f"FETCH_LIMIT is set to {fetch_limit}.")
    except ValueError:
        fetch_limit = 0
        logger.warning(
            "FETCH_LIMIT in .env is not a valid integer. Defaulting to 0."
        )

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
        logger.info(f"Will be fetching details {total_ads} job ads")

    logger.info("Detail feching started...")

    time.sleep(5)

    for job_ad in ads_to_process:
        job_data = parse_job_details(job_ad["job_link"])
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
