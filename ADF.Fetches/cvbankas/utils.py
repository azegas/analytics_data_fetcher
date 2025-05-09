import requests
from config import URL
from log_config import logger
from dotenv import load_dotenv

from extractors.extractor_other import extract_details_of_many
from extractors.extractor_article import ExtractorArticle
from extractors.extractor_job import ExtractorJob
from db_stuff import get_existing_job_ids_from_db

# TODO FIX UTILS2, same place. just somehow without circular dependencies
from utils2 import extract_after_last_slash


extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()


def procesiukaszn():

    checked_articles = []
    article_details = []

    # Fetch existing ads from the DB
    existing_job_ads = get_existing_job_ids_from_db()

    # Find pages that have expiring ads
    pages_with_expiring_ads = find_pages_with_expiring_ads()

    # Go though pages with expiring ads and list the articles that we will need to take the details of
    for page_number in pages_with_expiring_ads:

        checked_article = check_article(page_number, existing_job_ads)

        checked_articles.extend(checked_article)

    # Extract details of the articles
    article_details = extract_details_of_many(checked_articles)

    return article_details


def find_pages_with_expiring_ads():
    pages_with_expiring_ads = []

    try:
        response = requests.get(URL)
        response.raise_for_status()

        last_page_number = extractor_article.extract_max_page_number(response)

        for current_page_number in range(last_page_number, 0, -1):

            page_has_expiring_ads = check_if_page_has_expiring_ads(
                current_page_number
            )

            if page_has_expiring_ads:
                logger.info(
                    f"Page {current_page_number} has expiring ads. Adding to the list"
                )
                pages_with_expiring_ads.append(current_page_number)
            else:
                logger.info(
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


def check_article(page_number, existing_job_ids):
    url = f"{URL}/?page={page_number}"

    response = requests.get(url)
    response.raise_for_status()

    articles = extractor_article.extract_articles(response)

    ok_job_summaries = []

    repeating_job_count = 0

    for job in articles:
        hours_left = extractor_article.extract_hours_left(job)
        job_id = extract_after_last_slash(extractor_article.extract_link(job))
        logger.debug(f"Checking job ID: {job_id}")
        if job_id not in existing_job_ids:
            ok_job_summary = {
                "job_id": job_id,
                "job_link": extractor_article.extract_link(job),
                "hours_left": hours_left,
                "from_page": page_number,
            }
            ok_job_summaries.append(ok_job_summary)
        else:
            logger.info(
                f"Job ID {job_id} already exists in the database. Skipping."
            )
            repeating_job_count += 1

    logger.info(
        f"Number of articles on page {page_number}: {len(articles)}, repeating ones - {repeating_job_count}"
    )

    return ok_job_summaries


def check_if_page_has_expiring_ads(page_number):
    url = f"{URL}/?page={page_number}"

    response = requests.get(url)
    response.raise_for_status()

    articles = extractor_article.extract_articles(response)

    page_has_expiring_ads = False

    for article in articles:
        hours_left = extractor_article.extract_hours_left(article)
        if hours_left:
            page_has_expiring_ads = True
            break

    return page_has_expiring_ads
