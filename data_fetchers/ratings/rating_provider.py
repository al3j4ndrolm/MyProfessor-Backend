from datetime import datetime, timedelta
from supabase import Client
from database import professors_db
from database import db_keys
from helpers.data import data_keys, data_creators
from data_fetchers.ratings.rmp import get_rmp_data
from logger import logger

def get_ratings_and_merge(supabase: Client, classes_one_department: dict, school: str, rmp_code: str, department_code: str) -> dict:
    for course_code, classes_one_course in classes_one_department.items():
        for professor_identifier, professor_data in classes_one_course.items():
            professor_name, professor_email = data_creators.parse_professor_identifier(professor_identifier)
            rmp_data = get_rating_data(supabase, school, department_code, professor_name, professor_email, rmp_code)
            if rmp_data:
                professor_data[data_keys.PROFESSOR_RATING_KEY] = rmp_data[data_keys.PROFESSOR_RATING_KEY]
                professor_data[data_keys.PROFESSOR_DIFFICULTY_KEY] = rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY]
                professor_data[data_keys.PROFESSOR_RECOMMEND_KEY] = rmp_data[data_keys.PROFESSOR_RECOMMEND_KEY]
                professor_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY] = rmp_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY]

def get_rating_data(supabase: Client, school: str, department: str, professor_name: str, professor_email: str, rmp_code: str) -> dict | None:
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
    if professor_entry and not professors_db.should_update(professor_entry):
        logger.debug(f"Returning professor {professor_name} in `professors` table.")
        return {
            data_keys.PROFESSOR_RATING_KEY: professor_entry[db_keys.KEY_RMP_RATING],
            data_keys.PROFESSOR_REVIEW_COUNT_KEY: professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT],
            data_keys.PROFESSOR_DIFFICULTY_KEY: professor_entry[db_keys.KEY_RMP_DIFFICULTY],
            data_keys.PROFESSOR_RECOMMEND_KEY: professor_entry[db_keys.KEY_RMP_RECOMMEND]
        }

    logger.debug(f"Searching for professor {professor_name} in RMP ...")
    rmp_data = get_rmp_data(professor_name, rmp_code)
    if rmp_data:
        logger.info(f"Saving professor {professor_name} in `professors` table.")
        professors_db.save_one_entry(supabase, school, department, professor_name, professor_email, rmp_data)
        del rmp_data[data_keys.PROFESSOR_LINK_KEY]
        del rmp_data[data_keys.PROFESSOR_SCORE_KEY]
        
        return rmp_data
    
    logger.debug(f"No professor {professor_name} found in RMP.")
    return None