import requests
from bs4 import BeautifulSoup
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path (for log_config)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_config import logger

pagesToFetch = 2  # how many pages to fetch?

load_dotenv()


def fetch_cvbankas_jobs():
    logger.info("Fetching CVBankas jobs...")
    jobs = []

    for page in range(1, pagesToFetch):

        url = f"https://en.cvbankas.lt/?page={page}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            articles = find_all_articles(response)

            breakpoint()

            for job in articles:

                job_data = {
                    "job_id": extract_id(job),
                    "link": extract_link(job),
                    "title": extract_title(job),
                    "company": extract_company(job),
                    "salary": extract_salary(job),
                    "posted": extract_when_posted(job),
                    "city": extract_city(job),
                }
                jobs.append(job_data)

        except Exception as e:
            logger.error(f"Error fetching data for page {page}: {e}")

    logger.info(f"Fetched {len(jobs)} job listings")
    return jobs


def find_all_articles(response):
    soup = BeautifulSoup(response.text, "html.parser")
    job_listings = soup.find_all("article", class_="list_article")
    return job_listings


def extract_link(job):
    job_link_tag = job.find("a", href=True)
    return job_link_tag["href"] if job_link_tag else None


def extract_id(job):
    return job.get("id", "").replace("job_ad_", "")


def extract_title(job):
    return job.find("h3", class_="list_h3").text.strip()


def extract_company(job):
    company_elem = job.find("span", class_="dib mt5 mr5")
    if company_elem:
        return company_elem.text.strip()
    return "N/A"


def extract_salary(job):
    salary_elem = job.find("span", class_="salary_amount")
    if not salary_elem:
        return "N/A"

    salary = salary_elem.text.strip()
    salary_period = job.find("span", class_="salary_period")
    salary_type = job.find("span", class_="salary_calculation")

    if salary_period and salary_type:
        return f"{salary} {salary_period.text.strip()} ({salary_type.text.strip()})"
    return salary


def extract_when_posted(job):
    time_elem = job.find("span", class_="txt_list_2")
    if time_elem:
        return time_elem.text.strip()
    else:
        important_elem = job.find("span", class_="txt_list_important")
        return important_elem.text.strip() if important_elem else None


def extract_city(job):
    city_elem = job.find("span", class_="list_city")
    return city_elem.text.strip() if city_elem else "N/A"


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


def main():
    jobs = fetch_cvbankas_jobs()
    save_cvbankas_jobs(jobs)


if __name__ == "__main__":
    main()
