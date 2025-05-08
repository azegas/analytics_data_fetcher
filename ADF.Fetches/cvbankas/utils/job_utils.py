import requests
from config import URL
from dotenv import load_dotenv
from extractors.extractor_article import ExtractorArticle
from extractors.extractor_job import ExtractorJob
from log_config import logger

extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()


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
