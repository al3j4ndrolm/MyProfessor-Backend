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
from database import schools_db, courses_db, classes_db
from database.schools_db import SchoolStatus
from database import db_keys
from helpers.data import data_keys, data_creators
from data_fetchers.ratings.rating_provider import get_ratings_and_merge
from logger import logger

def main(supabase: Client):
    schools = schools_db.get(supabase, status=SchoolStatus.MAINTENANCE.value)
    
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
                new_classes_data_per_course = {}
                for professor_name, professor_data in classes_per_course.items():
                    # logger.info(f"Processing professor {professor_name} ...")
                    if " email:" in professor_name:
                        break
                    elif "@" in professor_name:
                        # Extract email from the last parentheses
                        last_open_paren = professor_name.rfind("(")
                        last_close_paren = professor_name.rfind(")")
                        
                        if last_open_paren != -1 and last_close_paren != -1 and last_close_paren > last_open_paren:
                            # Extract the email (content of last parentheses)
                            professor_email = professor_name[last_open_paren + 1:last_close_paren]
                            # Extract the name (everything before the last parentheses)
                            professor_name = professor_name[:last_open_paren].strip()
                        else:
                            # Fallback if no valid parentheses found
                            professor_email = None
                    else:
                        professor_email = professor_data[data_keys.PROFESSOR_EMAIL_KEY] if data_keys.PROFESSOR_EMAIL_KEY in professor_data else None
                        del professor_data[data_keys.PROFESSOR_EMAIL_KEY]
                    professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)
                    # logger.info(f"Processed professor key from [{professor_name}] into [{professor_identifier}].")
                    new_classes_data_per_course[professor_identifier] = professor_data
                classes_per_department[course_code] = new_classes_data_per_course

            logger.info(f"Finished processing department {department_code} in term {term_code}.")
            get_ratings_and_merge(supabase, classes_per_department, school_name, rmp_code, department_code)
            classes_db.save_one_entry(supabase, classes_per_department, school_name, term_code, department_code)
            logger.info(f"Updated classes data for {term_code} - {department_code}.")
        logger.info(f"Updated classes data for {school_name}.")

if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    main(supabase)