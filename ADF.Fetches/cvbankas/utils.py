import requests
from other_stuff.config import URL
from other_stuff.log_config import logger
from dotenv import load_dotenv

from extractors.extractor_other import extract_details_of_many
from extractors.extractor_article import ExtractorArticle
from extractors.extractor_job import ExtractorJob
from db_stuff import get_existing_job_ids_from_db

from utils2 import extract_after_last_slash


extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()

# using sessions
# replaced response = requests.get(URL) to session = requests.Session()

# 🔍 Problem with requests.get() by itself
# When you use requests.get(URL) directly, what happens under the hood is:
# A new TCP connection is opened.
# The request is sent.
# The response is received.
# The connection is closed immediately after that.


# ✅ Why requests.Session() is better
# Using a Session object from the requests library gives you several key performance and feature advantages:
# Reuses TCP connections (Keep-Alive)
# When you make a request with a Session, it keeps the connection open.
# If you make another request to the same host, the connection is reused.
# This reduces the latency (waiting time) for new requests and saves CPU & memory.
session = requests.Session()


def process_expiring_job_ads():

    checked_articles = []
    article_details = []

    total_articles_count = 0
    total_repeating_articles_count = 0

    # Fetch existing ads from the DB
    existing_job_ads = get_existing_job_ids_from_db()

    # Find pages that have expiring ads
    pages_with_expiring_ads = find_pages_with_expiring_ads()

    # Go though pages with expiring ads and list the articles that we will need to take the details of
    for page_number in pages_with_expiring_ads:

        (
            checked_article,
            total_articles_in_page_count,
            total_repeating_articles_in_page_count,
        ) = check_articles_of_a_page(page_number, existing_job_ads)

        checked_articles.extend(checked_article)

        total_articles_count += total_articles_in_page_count
        total_repeating_articles_count += (
            total_repeating_articles_in_page_count
        )

    logger.info(
        f"There were total {total_articles_count} articles of which {total_repeating_articles_count} were repeating"
    )

    # Extract details of the articles
    article_details = extract_details_of_many(checked_articles)

    return article_details


def find_pages_with_expiring_ads():
    pages_with_expiring_ads = []

    try:
        response = session.get(URL)
        response.raise_for_status()

        last_page_number = extractor_article.extract_max_page_number(response)

        for current_page_number in range(last_page_number, 0, -1):

            page_has_expiring_ads = check_if_page_has_expiring_ads(
                current_page_number
            )

            if page_has_expiring_ads:
                logger.debug(
                    f"Page {current_page_number} has expiring ads. Adding to the list"
                )
                pages_with_expiring_ads.append(current_page_number)
            else:
                logger.debug(
                    f"Page {current_page_number} has no expiring ads. Stopping the search."
                )
                break

        logger.info(
            f"Found {len(pages_with_expiring_ads)} pages with expiring ads - {pages_with_expiring_ads}."
        )

        return pages_with_expiring_ads

    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return pages_with_expiring_ads


def check_articles_of_a_page(page_number, existing_job_ids):
    url = f"{URL}/?page={page_number}"

    response = session.get(url)
    response.raise_for_status()

    articles = extractor_article.extract_articles(response)

    ok_job_summaries = []

    total_articles_in_page_count = len(articles)
    total_repeating_articles_in_page_count = 0

    for article in articles:
        try:
            job_link = extractor_article.extract_link(article)
            job_id = extract_after_last_slash(job_link)
            hours_left = extractor_article.extract_hours_left(article)

            logger.debug(f"Checking job ID: {job_id}")

            if job_id not in existing_job_ids:
                ok_job_summary = {
                    "job_id": job_id,
                    "job_link": job_link,
                    "hours_left": hours_left,
                    "from_page": page_number,
                }
                ok_job_summaries.append(ok_job_summary)
            else:
                logger.debug(
                    f"Job ID {job_id} already exists in the database. Skipping."
                )
                total_repeating_articles_in_page_count += 1
        except Exception as e:
            logger.warning(f"Skipping job due to error: {e}")

    logger.info(
        f"Number of articles on page {page_number}: {len(articles)}, repeating ones - {total_repeating_articles_in_page_count}"
    )

    return (
        ok_job_summaries,
        total_articles_in_page_count,
        total_repeating_articles_in_page_count,
    )


def check_if_page_has_expiring_ads(page_number):
    url = f"{URL}/?page={page_number}"

    response = session.get(url)
    response.raise_for_status()

    articles = extractor_article.extract_articles(response)

    page_has_expiring_ads = False

    for article in articles:
        hours_left = extractor_article.extract_hours_left(article)
        if hours_left:
            page_has_expiring_ads = True
            break

    return page_has_expiring_ads
