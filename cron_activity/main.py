import schedule
import time
import subprocess
import os

import logging
logger = logging.getLogger(__name__)

from configs import SCHOOLS

def schools_data_fetcher():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)

    for school in SCHOOLS:
        logger.info(f"Fetching data for {school} ...")

        try:
            subprocess.run([
                "python", "-m", "data_fetchers.schools.schools_data_fetcher", "--schools", school  
            ], cwd=backend_dir, check=True)
            logger.info(f"Data fetched for {school} ...")

        except Exception as e:
            logger.error(f"Error fetching data for {school}: {e}")

schedule.every().day.at("01:01").do(schools_data_fetcher) 

# TO RUN LOCALLY ONLY: python -m cron_activity.main
while True:
    logger.info("Running scheduled tasks...")
    schedule.run_pending()
    logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scheduled tasks completed.")
    time.sleep(1)