from saving.sqlite_db_init import initialize_sqlite_db
from log_config import logger
import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def save_job_ads(jobs, save_location):
    try:
        if save_location == "LOCAL":
            save_to_json_locally(jobs)
        elif save_location == "SQLITE_DB":
            initialize_sqlite_db()
            save_to_sqlite_db(jobs)
        else:
            logger.error("something not right with saving location")
            return

    except IOError as e:
        logger.error(f"Failed to save data: {e}")


def save_to_json_locally(jobs):
    try:
        data_to_save = {
            "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "jobs": jobs,
        }

        base_dir = os.getenv("BASE_DIR", os.getcwd())
        file_path = os.path.join(base_dir, "data/cvbankas_ads.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        logger.info(f"Data saved to {file_path}")

    except IOError as e:
        logger.error(f"Failed to save data locally: {e}")


def save_to_sqlite_db(jobs):
    load_dotenv()
    base_dir = os.getenv("BASE_DIR", os.getcwd())
    db_path = os.path.join(base_dir, "data", "job_ads.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for job in jobs:
        try:
            # Insert job data into job_ads table
            cursor.execute(
                """
                INSERT INTO job_ads (
                    job_link, job_title, job_category, job_cities, job_views, job_applications,
                    job_salary, job_salary_period, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    job["job_link"],
                    job["job_title"],
                    job["job_category"],
                    job["job_cities"],
                    job["job_views"],
                    job["job_applications"],
                    job["job_salary"],
                    job["job_salary_period"],
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )

            # Get the last inserted job_ad id
            job_ad_id = cursor.lastrowid

            # Insert company details into company_details table
            company = job["company_details"]
            cursor.execute(
                """
                INSERT INTO company_details (
                    job_ad_id, company_name, average_salary, employee_count, revenue
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    job_ad_id,
                    company["company_name"],
                    company["average_salary"],
                    company["employee_count"],
                    company["revenue"],
                ),
            )

            conn.commit()

        except sqlite3.Error as e:
            # Log error and continue to the next job
            logger.error(f"Error inserting job ad {job['job_link']}: {e}")
            continue

    logger.info("Data saved to SQLite DB successfully.")

    conn.close()
