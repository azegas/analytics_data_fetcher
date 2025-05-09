import requests
from bs4 import BeautifulSoup
from other_stuff.log_config import logger
from extractors.extractor_job import ExtractorJob
from utils2 import extract_after_last_slash

extractor_job = ExtractorJob()


def parse_job_details(job_url):
    try:
        response = requests.get(job_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        job_stats = extractor_job.extract_job_statistics(soup, job_url)
        salary_details = extractor_job.extract_salary(soup, job_url)
        company_details = extractor_job.extract_company_details(soup, job_url)

        job_data = {
            "job_id": extract_after_last_slash(job_url),
            "job_link": job_url,
            "job_title": extractor_job.extract_title(soup, job_url),
            "job_category": extractor_job.extract_category(soup, job_url),
            "job_cities": extractor_job.extract_cities(soup, job_url),
            "job_views": job_stats["views"],
            "job_applications": job_stats["applications"],
            "job_salary": salary_details["salary"],
            "job_salary_period": salary_details["period"],
            "company_details": {
                "company_name": extractor_job.extract_company_name(
                    soup, job_url
                ),
                "average_salary": company_details.get("average_salary"),
                "employee_count": company_details.get("employee_count"),
                "revenue": company_details.get("revenue"),
            },
        }

        return job_data

    except Exception as e:
        logger.error(f"Error parsing job {job_url}: {e}")
        return None
