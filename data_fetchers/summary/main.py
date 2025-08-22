from supabase import Client
from database import summaries_db, schools_db, professors_db, db_keys
from logger import logger
from data_fetchers.summary.deepseek import DeepSeekSession
from data_fetchers.rmp.reviews.reviews import get_reviews, get_session

def update_summaries_table(supabase: Client):
    deepseek_session = DeepSeekSession()
    session = get_session()
    schools = _get_available_schools(supabase)

    for school in schools:
        rmp_links = professors_db.get_all_rmp_links_from_school(supabase, school)
        logger.info(f"Found {len(rmp_links)} RMP links for {school}")
        logger.info(f"RMP links: {rmp_links}")

        for rmp_link in list(rmp_links):
            reviews = get_reviews(rmp_link, school, session)
            if reviews is None:
                logger.info(f"No reviews found for {rmp_link}")
                continue

            reviews_count = len(reviews[2]['data']['node']['ratings']['edges'])
            logger.info(f"Found {reviews_count} reviews for {rmp_link}")
            summary = deepseek_session.get_summary(reviews)
            summaries_db.save_one_entry(supabase, rmp_link, summary)
            logger.info(f"Saved summary for {rmp_link} in {school}")

def _get_available_schools(supabase: Client) -> list[str]:
    # schools = schools_db.get(supabase)
    # school_names = [school[db_keys.SCHOOL_KEY_SCHOOL_NAME] for school in schools]
    # return school_names
    return ["Testing School"]