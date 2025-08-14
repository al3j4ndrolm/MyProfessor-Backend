from datetime import datetime, timedelta
from supabase import Client
from database import professors_db
from database import db_keys
from data_fetchers.ratings.rating_configs import RMP_DEFAULTS
from helpers.data import data_keys, data_creators
from data_fetchers.ratings.rmp import get_rmp_data
from data_fetchers.ai_summary.ai_summary import generate_ai_summary
from logger import logger

def get_ratings_and_merge(supabase: Client, classes_one_department: dict, school: str, rmp_code: str, department_code: str, rescan_null: bool = False) -> dict:
    for course_code, classes_one_course in classes_one_department.items():
        for professor_identifier, professor_data in classes_one_course.items():
            professor_name, professor_email = data_creators.parse_professor_identifier(professor_identifier)
            rmp_data = get_rating_data(supabase, school, department_code, professor_name, professor_email, rmp_code, rescan_null)
            professor_data[data_keys.PROFESSOR_RMP_DATA_KEY] = rmp_data

def get_rating_data(supabase: Client, school: str, department: str, professor_name: str, professor_email: str, rmp_code: str, rescan_null: bool) -> dict:
    """
    Example of rmp_data:
    {
        "link": "/professor/1234567890",
        "score": 0.988,
        "rating": "4.5",
        "reviewsCount": "100",
        "difficulty": "3.0",
        "recommend": "90"
    }

    Example of return value:
    {
        "rating": "4.5",
        "reviewsCount": "100",
        "difficulty": "3.0",
        "recommend": "90"
    }
    """

    logger.debug(f"Checking if professor {professor_name} in {school} {department} is in `professors` table ...")
    professor_entry = professors_db.get_one_entry(supabase, school, department, professor_name, professor_email)
    if professor_entry:
        should_search = False
        if rescan_null:
            should_search = professor_entry[db_keys.KEY_RMP_LINK] is None
        should_search = should_search or professors_db.should_update(professor_entry)
        
        # Check if we need to generate AI summary for existing professor
        needs_ai_summary = professor_entry.get(db_keys.KEY_AI_SUMMARY) is None and professor_entry.get(db_keys.KEY_RMP_LINK) is not None
        
        if not should_search and not needs_ai_summary:
            logger.debug(f"Returning professor {professor_name} in `professors` table.")
            return {
                data_keys.PROFESSOR_RATING_KEY: professor_entry[db_keys.KEY_RMP_RATING],
                data_keys.PROFESSOR_REVIEW_COUNT_KEY: professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT],
                data_keys.PROFESSOR_DIFFICULTY_KEY: professor_entry[db_keys.KEY_RMP_DIFFICULTY],
                data_keys.PROFESSOR_RECOMMEND_KEY: professor_entry[db_keys.KEY_RMP_RECOMMEND],
                db_keys.KEY_AI_SUMMARY: professor_entry.get(db_keys.KEY_AI_SUMMARY)
            }
        
        # If we need to generate AI summary, continue to the RMP search section
        if needs_ai_summary:
            logger.info(f"Professor {professor_name} exists but needs AI summary. Fetching RMP data...")
            rmp_data = get_rmp_data(professor_name, rmp_code) if not is_staff(professor_name) else None
            if rmp_data and rmp_data.get(data_keys.PROFESSOR_LINK_KEY):
                # Generate AI summary for existing professor
                try:
                    logger.info(f"Generating AI summary for existing professor {professor_name}...")
                    ai_summary = generate_ai_summary(
                        professor_name=professor_name,
                        school=school,
                        professor_email=professor_email,
                        rmp_link=rmp_data.get(data_keys.PROFESSOR_LINK_KEY)
                    )
                    if ai_summary:
                        # Update the existing professor record with AI summary
                        supabase.table("professors").update({db_keys.KEY_AI_SUMMARY: ai_summary})\
                            .eq("email", professor_email)\
                            .eq("professor_name", professor_name)\
                            .eq("school", school)\
                            .eq("department", department)\
                            .execute()
                        logger.info(f"Successfully updated AI summary for existing professor {professor_name}")
                        return {
                            data_keys.PROFESSOR_RATING_KEY: professor_entry[db_keys.KEY_RMP_RATING],
                            data_keys.PROFESSOR_REVIEW_COUNT_KEY: professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT],
                            data_keys.PROFESSOR_DIFFICULTY_KEY: professor_entry[db_keys.KEY_RMP_DIFFICULTY],
                            data_keys.PROFESSOR_RECOMMEND_KEY: professor_entry[db_keys.KEY_RMP_RECOMMEND],
                            db_keys.KEY_AI_SUMMARY: ai_summary
                        }
                except Exception as e:
                    logger.error(f"Error generating AI summary for existing professor {professor_name}: {e}")
            
            # If AI summary generation failed, return existing data
            return {
                data_keys.PROFESSOR_RATING_KEY: professor_entry[db_keys.KEY_RMP_RATING],
                data_keys.PROFESSOR_REVIEW_COUNT_KEY: professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT],
                data_keys.PROFESSOR_DIFFICULTY_KEY: professor_entry[db_keys.KEY_RMP_DIFFICULTY],
                data_keys.PROFESSOR_RECOMMEND_KEY: professor_entry[db_keys.KEY_RMP_RECOMMEND],
                db_keys.KEY_AI_SUMMARY: professor_entry.get(db_keys.KEY_AI_SUMMARY)
            }

    logger.debug(f"Not found, searching for professor {professor_name} in RMP ...")
    
    if is_staff(professor_name): # if the professor is a staff, we don't need to fetch the rating data
        rmp_data = None
    else:
        rmp_data = get_rmp_data(professor_name, rmp_code)
    
    if not rmp_data:
        logger.debug(f"No professor {professor_name} found in RMP.")
        rmp_data = {
            data_keys.PROFESSOR_LINK_KEY: None,
            data_keys.PROFESSOR_SCORE_KEY: None,
            data_keys.PROFESSOR_RATING_KEY: RMP_DEFAULTS[data_keys.PROFESSOR_RATING_KEY],
            data_keys.PROFESSOR_REVIEW_COUNT_KEY: RMP_DEFAULTS[data_keys.PROFESSOR_REVIEW_COUNT_KEY],
            data_keys.PROFESSOR_DIFFICULTY_KEY: RMP_DEFAULTS[data_keys.PROFESSOR_DIFFICULTY_KEY],
            data_keys.PROFESSOR_RECOMMEND_KEY: RMP_DEFAULTS[data_keys.PROFESSOR_RECOMMEND_KEY]
        }
    
    # Generate AI summary if we have valid RMP data and professor email
    if rmp_data and rmp_data.get(data_keys.PROFESSOR_LINK_KEY) and professor_email:
        try:
            logger.info(f"Generating AI summary for {professor_name}...")
            ai_summary = generate_ai_summary(
                professor_name=professor_name,
                school=school,
                professor_email=professor_email,
                rmp_link=rmp_data.get(data_keys.PROFESSOR_LINK_KEY)
            )
            if ai_summary:
                rmp_data[db_keys.KEY_AI_SUMMARY] = ai_summary
                logger.info(f"Successfully generated AI summary for {professor_name}")
            else:
                logger.warning(f"Failed to generate AI summary for {professor_name}")
        except Exception as e:
            logger.error(f"Error generating AI summary for {professor_name}: {e}")
    
    logger.info(f"Saving professor {professor_name} in `professors` table.")
    professors_db.save_one_entry(supabase, school, department, professor_name, professor_email, rmp_data)
    del rmp_data[data_keys.PROFESSOR_LINK_KEY]
    del rmp_data[data_keys.PROFESSOR_SCORE_KEY]
    return rmp_data

def is_staff(professor_name: str) -> bool:
    name_lower = professor_name.lower().strip()
    return (
        name_lower == "staff" or 
        name_lower.startswith("staff,")
    )