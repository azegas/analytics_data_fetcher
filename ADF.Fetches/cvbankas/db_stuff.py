from log_config import logger
import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    base_dir = os.getenv("BASE_DIR", os.getcwd())
    db_path = os.path.join(base_dir, "data", "job_ads.db")
    conn = sqlite3.connect(db_path)
    return conn


def initialize_sqlite_db():
    """Initialize SQLite DB and create tables if they don't exist."""

    load_dotenv()

    base_dir = os.getenv("BASE_DIR", os.getcwd())
    db_path = os.path.join(base_dir, "data", "job_ads.db")

    if os.path.exists(db_path):
        logger.info("SQLITE database already exists.")
        return  # DB already exists, no need to reinitialize

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create job_ads table
    cursor.execute(
        """
        CREATE TABLE job_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            job_link TEXT,
            job_title TEXT,
            job_category TEXT,
            job_cities TEXT,
            job_views TEXT,
            job_applications TEXT,
            job_salary TEXT,
            job_salary_period TEXT,
            fetched_at TEXT
        )
    """
    )

    # Create company_details table
    cursor.execute(
        """
        CREATE TABLE company_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_ad_id INTEGER,
            company_name TEXT,
            average_salary TEXT,
            employee_count TEXT,
            revenue TEXT,
            FOREIGN KEY(job_ad_id) REFERENCES job_ads(id)
        )
    """
    )

    logger.info("SQLITE database initialized and tables created.")

    conn.commit()
    conn.close()


def save_to_sqlite_db(jobs):
    conn = get_db_connection()
    cursor = conn.cursor()

    for job in jobs:
        try:
            # Insert job data into job_ads table
            cursor.execute(
                """
                INSERT INTO job_ads (
                    job_id, job_link, job_title, job_category, job_cities, job_views, job_applications,
                    job_salary, job_salary_period, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_id"],
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

    count_records_in_db()

    conn.close()


def get_existing_job_ids_from_db():
    """Retrieve existing job IDs from the database."""

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT job_id FROM job_ads")
        existing_job_ids = {row[0] for row in cursor.fetchall()}
        logger.info(f"Existing job IDs in database: {existing_job_ids}")
        return existing_job_ids
    except sqlite3.Error as e:
        logger.error(f"Error retrieving existing job IDs: {e}")
        return set()
    finally:
        conn.close()


def count_records_in_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM job_ads")
        count = cursor.fetchone()[0]
        logger.info(f"Total records in job_ads table: {count}")
        return count
    except sqlite3.Error as e:
        logger.error(f"Error counting records: {e}")
        return 0
    finally:
        conn.close()


def save_job_ads(jobs, save_location):
    if not jobs:
        logger.error("No jobs data provided to save.")
        return

    try:
        if save_location == "LOCAL":
            save_to_json_locally(jobs)
        elif save_location == "SQLITE_DB":
            save_to_sqlite_db(jobs)
        else:
            logger.error("Something is not right with the saving location.")
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


def decide_upon_saving_location(saving_location):
    if not saving_location:
        logger.error("DATA_SAVE_LOCATION is not set in .env, go do that first")
        return

    if saving_location not in {"LOCAL", "SQLITE_DB"}:
        logger.error(
            "DATA_SAVE_LOCATION must be either 'LOCAL' or 'SQLITE_DB'"
        )
        return
    else:
        logger.info(f"Saving location is set to {saving_location}")
