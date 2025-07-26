from supabase import create_client, Client
from database import schools_db, courses_db, classes_db, professors_db
from helpers.data import data_keys
from helpers.data.data_creators import get_professors, get_professor_from_rmp_data
from data_fetchers.ratings.rmp import get_rmp_data
from database import db_keys
from logger import logger
from dotenv import load_dotenv
import os

def main(supabase: Client):
    schools = schools_db.get(supabase)
    
    for school_entry in schools:
        school_name = school_entry[db_keys.KEY_SCHOOL_NAME]
        rmp_code = school_entry[db_keys.KEY_RMP_CODE]

        departments_dict = courses_db.get(supabase, school_name)
        if not departments_dict:
            logger.info(f"No departments stored in database for {school_name} yet.")
            continue
        
        departments = departments_dict.keys()
        for department in departments:
            # get all the professors for this school/department from `professors` table
            professor_entries = professors_db.get_all(supabase, school_name, department)
            if not professor_entries:
                logger.info(f"No professors stored in database for {school_name} - {department} yet.")
                continue
            
            logger.info(f"Fetching RMP data for {len(professor_entries)} professors in {school_name} - {department}...")
            # Call RMP for this school/department
            rmp_data_table = get_rmp_data(list(professor_entries.keys()), rmp_code)
            
            _update_professors(supabase, professor_entries, rmp_data_table)
            logger.info(f"Updated {len(rmp_data_table)} professors in {school_name} - {department}.")

def _update_professors(supabase: Client, professor_entries: dict, rmp_data_table: dict):
    to_update = []
    
    for professor_name, professor_data in rmp_data_table.items():
        professor_data = get_professor_from_rmp_data(professor_data)
        professor_entry = professor_entries[professor_name].copy()

        professor_entry[db_keys.KEY_RMP_DIFFICULTY] = professor_data[data_keys.PROFESSOR_DIFFICULTY_KEY]
        professor_entry[db_keys.KEY_RMP_RATING] = professor_data[data_keys.PROFESSOR_RATING_KEY]
        professor_entry[db_keys.KEY_RMP_RECOMMEND] = professor_data[data_keys.PROFESSOR_RECOMMEND_KEY]
        professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT] = professor_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY]
        professor_entry[db_keys.KEY_RMP_SCORE] = professor_data[data_keys.PROFESSOR_SCORE_KEY]
        professor_entry[db_keys.KEY_RMP_LINK] = professor_data[data_keys.PROFESSOR_LINK_KEY]

        if professor_entry != professor_entries[professor_name]:
            to_update.append(professor_entry)
    
    # update all updated professors for one school/department at once
    professors_db.update(supabase, to_update)

if __name__ == "__main__":
    # Initialize Supabase client
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    main(supabase)