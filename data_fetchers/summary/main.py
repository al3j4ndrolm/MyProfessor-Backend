from supabase import create_client, Client
from database import summaries_db, schools_db, professors_db, db_keys
from database.schools_db import SchoolStatus
from logger import logger
from data_fetchers.summary.deepseek import DeepSeekSession
from data_fetchers.rmp.reviews.reviews import get_reviews, get_session
import requests
import openai
import os
from dotenv import load_dotenv

def update_summaries_table(supabase: Client, deepseek_session: DeepSeekSession, session: requests.Session):
    schools = schools_db.get(supabase, [SchoolStatus.TESTING])

    for school in schools:
        school_name = school[db_keys.SCHOOL_KEY_SCHOOL_NAME]
        rmp_links = professors_db.get_unique_rmp_links(supabase, school_name)
        logger.info(f"Found {len(rmp_links)} RMP links for {school_name}, now processing...")

        for rmp_link in list(rmp_links):
            summary = _get_summary(rmp_link, session, deepseek_session)
            if summary:
                summaries_db.save_one_entry(supabase, rmp_link, summary)
                logger.info(f"Saved summary for {rmp_link}")
            else:
                logger.warning(f"Failed to get summary for {rmp_link}")
                summaries_db.save_one_entry(supabase, rmp_link, {})

def _get_summary(rmp_link, session, deepseek_session: DeepSeekSession) -> dict | None:
    reviews = get_reviews(rmp_link, session)
    if reviews == {}:
        logger.warning(f"No reviews found for {rmp_link}")
        return {}

    try:
        summary = deepseek_session.get_summary(reviews)
        return summary
    except openai.BadRequestError as e:
        # TODO: retry with less reviews
        return {}

if __name__ == "__main__":
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    session = get_session()
    deepseek_session = DeepSeekSession()
    
    update_summaries_table(supabase, deepseek_session, session)