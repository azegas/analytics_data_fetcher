import requests
from bs4 import BeautifulSoup
import re
from log_config import logger


class ExtractorArticle:

    @staticmethod
    def extract_link(job):
        try:
            job_link_tag = job.find("a", href=True)
            if not job_link_tag:
                logger.warning("No link found in job element.")
                return ""
            return job_link_tag["href"]

        except Exception as e:
            logger.error(f"Failed to extract job link: {e}")
            return ""

    @staticmethod
    def extract_hours_left(job):
        try:
            important_texts = job.find_all(class_="txt_list_important")
            if not important_texts:
                logger.debug("No important text elements found.")
                return ""

            for text_element in important_texts:
                text = text_element.get_text(strip=True)
                match = re.search(
                    r"(\d+)\s+hours?\s+left", text, re.IGNORECASE
                )
                if match:
                    return int(match.group(1))

            return ""

        except Exception as e:
            logger.error(f"Failed to extract hours left: {e}")
            return ""

    @staticmethod
    def extract_articles(response):
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            job_listings = soup.find_all("article", class_="list_article")
            if not job_listings:
                logger.warning("No job listings found.")
            return job_listings

        except Exception as e:
            logger.error(f"Failed to extract job articles: {e}")
            return []

    @staticmethod
    def extract_max_page_number(response):
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            pagination_ul = soup.find("ul", class_="pages_ul_inner")
            if not pagination_ul:
                logger.warning("Pagination element not found.")
                return ""

            li_elements = pagination_ul.find_all("li")
            if not li_elements:
                logger.warning("No <li> elements found in pagination.")
                return ""

            last_li = li_elements[-1]
            last_a_tag = last_li.find("a")
            if not last_a_tag:
                logger.warning("Last page <a> tag not found.")
                return ""

            last_page_number = last_a_tag.get_text(strip=True)
            logger.info(f"Found last page number: {last_page_number}")
            return int(last_page_number)

        except Exception as e:
            logger.error(f"Failed to extract max page number: {e}")
            return ""
