import requests
from bs4 import BeautifulSoup


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
