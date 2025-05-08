from utils.job_utils import (
    create_list_of_expiring_job_ads,
)

from extractors.extractor_other import (
    extract_details_of_many,
    extract_details_of_one,
)

from saving.saving_logic import save_job_ads
from dotenv import load_dotenv
import os
from log_config import logger


def main():
    """Main function to fetch and save job ads."""

    load_dotenv()

    fetch_specific = os.getenv("FETCH_SPECIFIC", "")
    saving_location = os.getenv("DATA_SAVE_LOCATION")

    if not saving_location:
        logger.error("DATA_SAVE_LOCATION is not set in .env, go do that first")
        return

    if saving_location not in {"LOCAL", "SQLITE_DB"}:
        logger.error(
            "DATA_SAVE_LOCATION must be either 'LOCAL' or 'SQLITE_DB'"
        )
        return

    if fetch_specific:
        expiring_job_ads_details = [extract_details_of_one(fetch_specific)]
    else:
        expiring_job_ads_list = create_list_of_expiring_job_ads()

        if not expiring_job_ads_list:
            logger.info("No expiring job ads found. Stopping the script.")
            return

        expiring_job_ads_details = extract_details_of_many(
            expiring_job_ads_list
        )

    save_job_ads(expiring_job_ads_details, saving_location)


if __name__ == "__main__":
    main()
