import requests
from bs4 import BeautifulSoup
import re
from log_config import logger


def extract_hours_left(job):
    # Find all elements with the class 'txt_list_important' within the job ad
    important_texts = job.find_all(class_="txt_list_important")

    for text_element in important_texts:
        text = text_element.get_text(strip=True)

        # Use a regular expression to find the number of hours
        match = re.search(r"(\d+)\s+hours?\s+left", text, re.IGNORECASE)
        if match:
            hours_left = int(match.group(1))
            return hours_left

    return None


def extract_max_page_number(response):
    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the <ul> with class "pages_ul_inner"
    pagination_ul = soup.find("ul", class_="pages_ul_inner")

    if pagination_ul:
        # Find all <li> elements within this <ul>
        li_elements = pagination_ul.find_all("li")

        # Get the last <li> element
        last_li = li_elements[-1]

        # Find the <a> tag within the last <li> element and return its text
        last_a_tag = last_li.find("a")
        if last_a_tag:
            last_page_number = last_a_tag.get_text(strip=True)
            logger.info(f"Found last page number: {last_page_number}")
            return int(last_page_number)

        return None


def extract_category_from_detail_page(job_url):
    try:
        response = requests.get(job_url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the <a> tag with 'darbo-pasiulymai' in the href attribute
        category_tag = soup.find(
            "a", href=lambda value: value and "darbo-pasiulymai" in value
        )

        # Extract and print the category text
        if category_tag:
            category = category_tag.get_text(strip=True)
            return category
        else:
            print("Category not found.")

    except requests.RequestException:
        return None


def extract_articles(response):
    soup = BeautifulSoup(response.text, "html.parser")
    job_listings = soup.find_all("article", class_="list_article")
    return job_listings


def extract_id(job):
    return job.get("id", "").replace("job_ad_", "")


def extract_link(job):
    job_link_tag = job.find("a", href=True)
    return job_link_tag["href"] if job_link_tag else None


def extract_title(job):
    return job.find("h3", class_="list_h3").text.strip()


def extract_company(job):
    company_elem = job.find("span", class_="dib mt5 mr5")
    return company_elem.text.strip() if company_elem else "N/A"


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
