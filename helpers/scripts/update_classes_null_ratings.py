import sys
from pathlib import Path

# Add the project root to Python path - this must be done before any other imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Also add the current directory to handle imports when running from MyProfessor-Backend
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))

from supabase import create_client, Client
from dotenv import load_dotenv
import os
from database import schools_db, courses_db, classes_db, professors_db
from database.schools_db import SchoolStatus
from database import db_keys
from helpers.data import data_keys, data_creators
from data_fetchers.ratings.rating_provider import get_ratings_and_merge
from logger import logger

def main(supabase: Client):
    schools = schools_db.get(supabase, status=SchoolStatus.SUPPORTED.value)
    
    for school_entry in schools:
        logger.info(f"Updating data fixing for {school_entry[db_keys.SCHOOL_KEY_SCHOOL_NAME]}")

        school_name = school_entry[db_keys.SCHOOL_KEY_SCHOOL_NAME]
        rmp_code = school_entry[db_keys.SCHOOL_KEY_RMP_CODE]

        classes_entries = classes_db.select_all_for_school(supabase, school_name)

        for classes_entry in classes_entries.data:
            term_code = classes_entry[db_keys.CLASSES_KEY_TERM]
            department_code = classes_entry[db_keys.CLASSES_KEY_DEPARTMENT]
            logger.info(f"Processing department {department_code} in term {term_code} ...")
            
            classes_per_department = classes_entry[db_keys.CLASSES_KEY_DATA]

            for course_code, classes_per_course in classes_per_department.items():
                for professor_identifier, professor_data in classes_per_course.items():
                    professor_name, professor_email = data_creators.parse_professor_identifier(professor_identifier)
                    need_update = not data_keys.PROFESSOR_RECOMMEND_KEY in professor_data\
                            or professor_data[data_keys.PROFESSOR_RECOMMEND_KEY] is None
                    if need_update:
                        logger.info(f"Found buggy professor {professor_name} in `professors` table.")

                        # professor_entry = professors_db.get_one_entry(supabase, school_name, department_code, professor_name, professor_email)
                        # if professor_entry is None or professor_entry[db_keys.KEY_RMP_RECOMMEND] is None:
                        #     logger.info(f"Found buggy professor {professor_name} in `professors` table.")

                        rmp_data = {
                            data_keys.PROFESSOR_RATING_KEY: -0.1,
                            data_keys.PROFESSOR_REVIEW_COUNT_KEY: 0,
                            data_keys.PROFESSOR_DIFFICULTY_KEY: 5.1,
                            data_keys.PROFESSOR_RECOMMEND_KEY: -1
                        }
                        professor_data.update(rmp_data)
                        # professors_db.save_one_entry(supabase, school_name, department_code, professor_name, professor_email, rmp_data)      
            # logger.info(f"Finished processing department {department_code} in term {term_code}.")
            # get_ratings_and_merge(supabase, classes_per_department, school_name, rmp_code, department_code)
            if need_update:
                classes_db.save_one_entry(supabase, classes_per_department, school_name, term_code, department_code)
                logger.info(f"Updated classes data for {term_code} - {department_code}.")
        logger.info(f"Updated classes data for {school_name}.")

if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    main(supabase)