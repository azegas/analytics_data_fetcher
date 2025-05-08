from log_config import logger


class ExtractorJob:
    @staticmethod
    def extract_category(soup, job_url):
        try:
            category_tag = soup.find(
                "a", href=lambda value: value and "darbo-pasiulymai" in value
            )
            if not category_tag:
                logger.debug(f"Category not found for ${job_url}.")
                return ""

            return category_tag.get_text(strip=True)

        except Exception as e:
            logger.error(f"Failed to extract category for {job_url}: {e}")
            return ""

    @staticmethod
    def extract_company_name(soup, job_url):
        try:
            company_tag = soup.find("h2", id="jobad_company_title")
            if not company_tag:
                logger.debug(f"Company title tag not found for ${job_url}.")
                return ""

            return company_tag.get_text(strip=True)

        except Exception as e:
            logger.error(f"Failed to extract company name for {job_url}: {e}")
            return ""

    @staticmethod
    def extract_cities(soup, job_url):
        try:
            address_span = soup.find("span", itemprop="address")
            if not address_span:
                logger.debug(f"Address span not found for ${job_url}.")
                return ""

            city_spans = address_span.find_all(
                "span", itemprop="addressLocality"
            )
            return ", ".join(span.get_text(strip=True) for span in city_spans)

        except Exception as e:
            logger.error(f"Failed to extract cities for ${job_url}: {e}")
            return ""

    @staticmethod
    def extract_salary(soup, job_url):
        try:
            salary_inner_tag = soup.find("span", class_="salary_inner")

            if not salary_inner_tag:
                logger.debug(f"Salary block not found for {job_url}.")
                return {"salary": "", "period": ""}

            salary_text_tag = salary_inner_tag.find(
                "span", class_="salary_text"
            )
            if not salary_text_tag:
                logger.debug(f"Salary text not found in {job_url}.")
                return {"salary": "", "period": ""}

            salary_amount = salary_text_tag.find(
                "span", class_="salary_amount"
            )
            salary_period = salary_text_tag.find(
                "span", class_="salary_period"
            )

            return {
                "salary": (
                    salary_amount.get_text(strip=True) if salary_amount else ""
                ),
                "period": (
                    salary_period.get_text(strip=True) if salary_period else ""
                ),
            }

        except Exception as e:
            logger.error(f"Failed to extract salary for {job_url}: {e}")
            return {"salary": "", "period": ""}

    @staticmethod
    def extract_title(soup, job_url):
        try:
            title_tag = soup.find("h1", id="jobad_heading1")
            if not title_tag:
                logger.debug(f"Title tag not found for {job_url}.")
                return ""

            return title_tag.get_text(strip=True)

        except Exception as e:
            logger.error(f"Failed to extract job title for {job_url}: {e}")
            return ""

    @staticmethod
    def extract_job_statistics(soup, job_link):
        try:
            if not soup:
                return {"views": "0", "applications": "0"}

            stats_aside = soup.find("aside", id="job_ad_statistics")
            if not stats_aside:
                logger.debug(
                    f"Statistics aside block not found for {job_link}."
                )
                return {"views": "0", "applications": "0"}

            stat_blocks = stats_aside.find_all("div", class_="jobad_stat")
            stats = []
            for block in stat_blocks:
                value_tag = block.find("strong", class_="jobad_stat_value")
                stats.append(
                    value_tag.get_text(strip=True) if value_tag else "0"
                )

            logger.debug(f"Found {stats}.")
            return {
                "views": stats[0] if len(stats) > 0 else "0",
                "applications": stats[1] if len(stats) > 1 else "0",
            }

        except Exception as e:
            logger.error(f"Failed to extract statistics for {job_link}: {e}")
            return {"views": "0", "applications": "0"}

    @staticmethod
    def extract_company_details(soup, job_url):
        try:
            company_info_div = soup.find(
                "div", class_="partners_company_info_main_info"
            )
            if not company_info_div:
                logger.debug(
                    f"Failed to extract company details for {job_url}. Company info div is None."
                )
                return {
                    "average_salary": "",
                    "employee_count": "",
                    "revenue": "",
                }

        except Exception as e:
            logger.error(
                f"Failed to extract company details for {job_url}: {e}"
            )
            return {
                "average_salary": "",
                "employee_count": "",
                "revenue": "",
            }

        def extract_value(class_name):
            try:
                block = company_info_div.find("div", class_=class_name)
                if not block:
                    return ""
                value = block.find(
                    "div", class_="partners_company_info_large_text"
                )
                return value.get_text(strip=True) if value else ""

            except Exception as e:
                logger.error(f"Failed to extract value for {class_name}: {e}")
                return ""

        return {
            "average_salary": extract_value(
                "partners_company_info_main_info_salary"
            ),
            "employee_count": extract_value(
                "partners_company_info_main_info_employees"
            ),
            "revenue": extract_value(
                "partners_company_info_main_info_revenue"
            ),
        }
