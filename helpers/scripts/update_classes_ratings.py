import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to Python path - this must be done before any other imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Also add the current directory to handle imports when running from MyProfessor-Backend
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))

from supabase import create_client, Client
from dotenv import load_dotenv
import os
from database import schools_db, classes_db
from database.schools_db import SchoolStatus
from database import db_keys
from data_fetchers.ratings.rating_provider import get_ratings_and_merge
from logger import logger

def main(supabase: Client):
    schools = schools_db.get(supabase, [SchoolStatus.FETCHING])
    
    for school_entry in schools:
        logger.info(f"Updating data fixing for {school_entry[db_keys.SCHOOL_KEY_SCHOOL_NAME]}")

        school_name = school_entry[db_keys.SCHOOL_KEY_SCHOOL_NAME]
        rmp_code = school_entry[db_keys.SCHOOL_KEY_RMP_CODE]

        classes_entries = classes_db.select_all_for_school(supabase, school_name)

        for classes_entry in classes_entries.data:
            updated_at = classes_entry[db_keys.CLASSES_KEY_UPDATED_AT]
            if is_updated_recently(updated_at):
                continue
            
            term_code = classes_entry[db_keys.CLASSES_KEY_TERM]
            department_code = classes_entry[db_keys.CLASSES_KEY_DEPARTMENT]
            logger.info(f"Processing department {department_code} in term {term_code} ...")
            
            classes_per_department = classes_entry[db_keys.CLASSES_KEY_DATA]
            get_ratings_and_merge(supabase, classes_per_department, school_name, rmp_code, department_code, rescan_null=True)
            
            classes_db.save_one_entry(supabase, classes_per_department, school_name, term_code, department_code)
            logger.info(f"Updated classes data for {term_code} - {department_code}.")
        logger.info(f"Updated classes data for {school_name}.")

def is_updated_recently(updated_at: str) -> bool:
    if updated_at is not None:
        try:
            updated_at_dt = datetime.fromisoformat(updated_at)
            if updated_at_dt.tzinfo is not None:
                updated_at_dt = updated_at_dt.replace(tzinfo=None)
            if updated_at_dt < datetime.now() - timedelta(hours=1):
                return True
        except (ValueError, TypeError):
            pass
    return False

if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    main(supabase)