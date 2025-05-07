import requests
from bs4 import BeautifulSoup
import re
from log_config import logger


class ExtractorArticle:
    @staticmethod
    def extract_link(job):
        job_link_tag = job.find("a", href=True)
        return job_link_tag["href"] if job_link_tag else None

    @staticmethod
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

    @staticmethod
    def extract_articles(response):
        soup = BeautifulSoup(response.text, "html.parser")
        job_listings = soup.find_all("article", class_="list_article")
        return job_listings

    @staticmethod
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
