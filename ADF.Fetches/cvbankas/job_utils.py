import requests
import json
import os
from datetime import datetime
from log_config import logger
from config import URL
from dotenv import load_dotenv
from extractor_article import ExtractorArticle
from extractor_job import ExtractorJob

extractor_article = ExtractorArticle()
extractor_job = ExtractorJob()

load_dotenv()

fetch_limit = int(os.getenv("TEST_A_FEW", 0))


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
                        "job_id": extractor_job.extract_id(job),
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


def extract_details(list_of_expiring_job_ads):
    logger.info(
        f"Received list of expiring job ads {len(list_of_expiring_job_ads)}",
    )

    total_ads = len(list_of_expiring_job_ads)
    fetched_count = 0
    jobs = []

    # Apply the limit only if it's greater than 0
    if fetch_limit > 0:
        ads_to_process = list_of_expiring_job_ads[:fetch_limit]
        logger.info(
            f"Fetching limit exists, fetching {fetch_limit} job ads..."
        )
    else:
        ads_to_process = list_of_expiring_job_ads
        logger.info(
            f"Fetching limit does not exists, fetching {len(list_of_expiring_job_ads)} job ads..."
        )

    logger.info("Fetch started...")

    for job_ad in ads_to_process:

        job_id = job_ad["job_id"]
        job_link = job_ad["link"]

        try:
            response = requests.get(job_link)
            response.raise_for_status()

            job_stats = extractor_job.extract_statistics(job_link)
            company_details = extractor_job.extract_company_details(job_link)
            salary_details = extractor_job.extract_salary(job_link)

            job_data = {
                "job_id": job_id,
                "job_link": job_link,
                "job_title": extractor_job.extract_title(job_link),
                "job_category": extractor_job.extract_category(job_link),
                "job_cities": extractor_job.extract_cities(job_link),
                "job_views": job_stats["views"],
                "job_applications": job_stats["applications"],
                "job_salary": salary_details["salary"],
                "job_salary_period": salary_details["period"],
                "company_details": {
                    "company_name": extractor_job.extract_company_name(
                        job_link
                    ),
                    "average_salary": company_details.get("average_salary"),
                    "employee_count": company_details.get("employee_count"),
                    "revenue": company_details.get("revenue"),
                },
            }
            jobs.append(job_data)
            fetched_count += 1
            remaining = total_ads - fetched_count
            logger.info(
                f"Fetched {fetched_count}/{total_ads} | Remaining: {remaining}"
            )

        except Exception as e:
            logger.error(f"Error fetching data for job ad {job_link}: {e}")

    logger.info(
        f"Finished fetching. Fetched {fetched_count} out of {total_ads}."
    )
    return jobs


def save_cvbankas_jobs_locally(jobs):
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
