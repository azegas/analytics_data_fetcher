import requests
from bs4 import BeautifulSoup
import re
from log_config import logger


class ExtractorJob:
    @staticmethod
    def extract_category(job_url):
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

    @staticmethod
    def extract_cities(job_url):
        try:
            response = requests.get(job_url)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the first <li> element with class 'nav_additional_li'
            nav_additional_li = soup.find("li", class_="nav_additional_li")

            if nav_additional_li:
                # Extract the text content of all <a> tags within this <li>
                city_links = nav_additional_li.find_all("a")
                cities = [link.get_text(strip=True) for link in city_links]

                # Join the city names into a single string separated by commas
                cities_string = ", ".join(cities)
                return cities_string
            else:
                print("nav_additional_li not found.")
                return None

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    @staticmethod
    def extract_id(job):
        return job.get("id", "").replace("job_ad_", "")

    @staticmethod
    def extract_title(job):
        return job.find("h3", class_="list_h3").text.strip()

    @staticmethod
    def extract_company(job):
        company_elem = job.find("span", class_="dib mt5 mr5")
        return company_elem.text.strip() if company_elem else "N/A"

    @staticmethod
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

    @staticmethod
    def extract_when_posted(job):
        time_elem = job.find("span", class_="txt_list_2")
        if time_elem:
            return time_elem.text.strip()
        else:
            important_elem = job.find("span", class_="txt_list_important")
            return important_elem.text.strip() if important_elem else None

    @staticmethod
    def extract_city(job):
        city_elem = job.find("span", class_="list_city")
        return city_elem.text.strip() if city_elem else "N/A"
