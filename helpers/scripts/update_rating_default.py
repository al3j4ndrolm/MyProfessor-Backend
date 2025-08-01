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
from database import db_keys
from typing import Optional
from database.professors_db import Professor
from datetime import datetime
from logger import logger

def main(supabase: Client):
    search_query = select_no_review(supabase)
    for professor_entry in search_query.data:
        professor = Professor(
            professor_name = professor_entry[db_keys.KEY_PROFESSOR_NAME],
            email = professor_entry[db_keys.KEY_EMAIL],
            school = professor_entry[db_keys.KEY_SCHOOL],
            department = professor_entry[db_keys.KEY_DEPARTMENT],
            rmp_difficulty = 5.1,
            rmp_rating = -0.1,
            rmp_recommend = -1,
            rmp_reviews_count = 0,
            rmp_score = professor_entry[db_keys.KEY_RMP_SCORE],
            rmp_link = professor_entry[db_keys.KEY_RMP_LINK],
            updated_at = datetime.now().isoformat()
        )   
        logger.info(f"Updating professor {professor_entry[db_keys.KEY_PROFESSOR_NAME]} from {professor_entry[db_keys.KEY_SCHOOL]} - {professor_entry[db_keys.KEY_DEPARTMENT]} ...")
        supabase.table("professors").update(professor.model_dump())\
            .eq(db_keys.KEY_PROFESSOR_NAME, professor_entry[db_keys.KEY_PROFESSOR_NAME])\
            .eq(db_keys.KEY_EMAIL, professor_entry[db_keys.KEY_EMAIL])\
            .eq(db_keys.KEY_SCHOOL, professor_entry[db_keys.KEY_SCHOOL])\
            .eq(db_keys.KEY_DEPARTMENT, professor_entry[db_keys.KEY_DEPARTMENT]).execute()

def select_no_review(supabase: Client) -> Optional[dict]:
    return supabase.table("professors")\
        .select("*")\
        .eq(db_keys.KEY_RMP_REVIEWS_COUNT, 0)\
        .execute()

if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    main(supabase)