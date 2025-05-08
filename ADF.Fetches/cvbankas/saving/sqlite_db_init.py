from log_config import logger
import os
import sqlite3
from dotenv import load_dotenv


def initialize_sqlite_db():
    """Initialize SQLite DB and create tables if they don't exist."""

    load_dotenv()

    base_dir = os.getenv("BASE_DIR", os.getcwd())
    db_path = os.path.join(base_dir, "data", "job_ads.db")

    if os.path.exists(db_path):
        return  # DB already exists, no need to reinitialize

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create job_ads table
    cursor.execute(
        """
        CREATE TABLE job_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
