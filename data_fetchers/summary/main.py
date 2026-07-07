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

            for rmp_link in rmp_links:
                logger.debug(f"Processing for professor {rmp_link}...")

                existing_summary = summaries_db.get_one_entry(supabase, rmp_link)
                if existing_summary:
                    summary = existing_summary[db_keys.SUMMARIES_KEY_SUMMARY]
                    if not summary:
                        logger.warning(f"None data exist in summary entry for {rmp_link}")
                        continue
                    professors_db.update_ai_summary(supabase, rmp_link, summary)
                else:
                    summary = _get_summary(rmp_link, session, deepseek_session)            
                    if summary:
                        summaries_db.save_one_entry(supabase, rmp_link, summary)    
                        professors_db.update_ai_summary(supabase, rmp_link, summary)
                        logger.info(f"Saved summary for {rmp_link}.")
                    
        else:
            # Get all RMP links (existing behavior)
            rmp_links = professors_db.get_unique_rmp_links(supabase, school_name)
            logger.info(f"Found {len(rmp_links)} RMP links for {school_name}, now processing...")

            for rmp_link in rmp_links:
                summary = _get_summary(rmp_link, session, deepseek_session)
                if summary:
                    summaries_db.save_one_entry(supabase, rmp_link, summary)
                    professors_db.update_ai_summary(supabase, rmp_link, summary)
                    logger.info(f"Saved summary for {rmp_link}.")

def _get_summary(rmp_link, session, deepseek_session: DeepSeekSession) -> dict | None:
    start_time = time.time()
    reviews = get_reviews(rmp_link, session)
    
    if reviews:
        try:
            summary = deepseek_session.get_summary(reviews)
            end_time = time.time()
            logger.debug(f"Time taken: {end_time - start_time:.1f} seconds.")
        except Exception as e:
            logger.error(f"Error in producing summary, error: {e}")

        if not summary:
            logger.warning(f"Not able to produce summary for professor {rmp_link}")
        return summary


if __name__ == "__main__":
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    session = setup_request_session()
    deepseek_session = DeepSeekSession(os.getenv("DEEPSEEK_API_KEY"))
    
    update_summaries_table(supabase, deepseek_session, session, only_add_new=True)