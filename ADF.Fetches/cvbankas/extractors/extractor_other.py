import os
import time

import requests
from bs4 import BeautifulSoup
from other_stuff.config import URL
from dotenv import load_dotenv
from extractors.extractor_article import ExtractorArticle
from extractors.extractor_job import ExtractorJob
from extractors.parser import parse_job_details
from other_stuff.log_config import logger
from other_stuff.send_email import send_email

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


def extract_details_of_many(
    list_of_expiring_job_ads,
    total_articles_count,
    total_repeating_articles_count,
):
    jobs = []
    fetched_count = 0
    count_of_expiring_job_ads = len(list_of_expiring_job_ads)

    if count_of_expiring_job_ads == 0:
        logger.info(
            f"Nothing to fetch, count_of_expiring_job_ads is {count_of_expiring_job_ads}."
        )

        email_subject = f"ADF: no new jobs, {total_repeating_articles_count} of {total_articles_count} are repeating ones."
        email_body = ""
        send_email(email_subject, email_body)

        logger.info("Stopping the script, BYE!")
        exit()

    logger.info(
        f"Will be fetching details for {count_of_expiring_job_ads} job ads"
    )

    time.sleep(3)

    logger.info("Detail feching started...")

    time.sleep(3)

    for job_ad in list_of_expiring_job_ads:
        job_data = parse_job_details(job_ad["job_link"])
        if job_data:
            jobs.append(job_data)
            fetched_count += 1
            logger.info(
                f"Fetched {job_data['job_id']} {fetched_count}/{count_of_expiring_job_ads} | Remaining: {count_of_expiring_job_ads - fetched_count}"
            )

    logger.info(
        f"Finished fetching. Fetched {fetched_count} out of {count_of_expiring_job_ads}."
    )
    return jobs
