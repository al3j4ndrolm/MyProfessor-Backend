from supabase import create_client, Client
from database import summaries_db, schools_db, professors_db, db_keys
from database.schools_db import SchoolStatus
from logger import logger
from data_fetchers.summary.deepseek import DeepSeekSession
from data_fetchers.rmp.reviews.reviews import get_reviews, setup_request_session
import requests
import os
from dotenv import load_dotenv
import time

def update_summaries_table(supabase: Client, deepseek_session: DeepSeekSession, session: requests.Session, only_add_new: bool = False):
    schools = schools_db.get(supabase, [SchoolStatus.SUPPORTED])

    for school in schools:
        school_name = school[db_keys.SCHOOL_KEY_SCHOOL_NAME]
        
        if only_add_new:
            # Use the function that gets RMP links without summaries
            rmp_links = professors_db.get_unique_rmp_links_without_summaries(supabase, school_name)
            logger.info(f"Found {len(rmp_links)} RMP links without summaries for {school_name}, now processing...")
        else:
            # Get all RMP links (existing behavior)
            rmp_links = professors_db.get_unique_rmp_links(supabase, school_name)
            logger.info(f"Found {len(rmp_links)} RMP links for {school_name}, now processing...")

        for rmp_link in rmp_links:
            # No need to check if summary exists when only_add_new=True since we already filtered
            summary = _get_summary(rmp_link, session, deepseek_session)
            if summary:
                summaries_db.save_one_entry(supabase, rmp_link, summary)
                logger.info(f"Saved summary for {rmp_link}.")

def _get_summary(rmp_link, session, deepseek_session: DeepSeekSession) -> dict | None:
    start_time = time.time()
    reviews = get_reviews(rmp_link, session)
    if not reviews:
        logger.warning(f"No reviews found for {rmp_link}")
        return None

    summary = deepseek_session.get_summary(reviews)
    end_time = time.time()
    logger.info(f"Time taken: {end_time - start_time:.1f} seconds.")
    return summary

if __name__ == "__main__":
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    session = setup_request_session()
    deepseek_session = DeepSeekSession()
    
    update_summaries_table(supabase, deepseek_session, session, only_add_new=True)