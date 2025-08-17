from deprecation import deprecated
from supabase import Client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from database import db_keys
from helpers.data import data_keys
from logger import logger

TABLE_NAME = "professors"

class Professor(BaseModel):
    professor_name: str
    email: Optional[str] = None
    school: str
    department: str
    rmp_difficulty: Optional[float] = None
    rmp_rating: Optional[float] = None
    rmp_recommend: Optional[int] = None
    rmp_reviews_count: Optional[int] = None
    rmp_score: Optional[float] = None
    rmp_link: Optional[str] = None

def get_one_entry(supabase: Client, school: str, department: str, professor_name: str, professor_email: str) -> Optional[Professor]:
    search_query = _select_one_query(supabase, school, department, professor_name, professor_email)
    
    return search_query.data[0] if search_query.data else None

def save_one_entry(supabase: Client, school: str, department: str, professor_name: str, professor_email: str, rmp_data: dict):
    search_query = _select_one_query(supabase, school, department, professor_name, professor_email)
    if not search_query.data:
        _add_one_entry(supabase, school, department, professor_name, professor_email, rmp_data)
    else:
        professor = Professor(
            professor_name = professor_name,
            email = professor_email,
            school = school,
            department = department,
            rmp_difficulty = rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY],
            rmp_rating = rmp_data[data_keys.PROFESSOR_RATING_KEY],
            rmp_recommend = rmp_data[data_keys.PROFESSOR_RECOMMEND_KEY],
            rmp_reviews_count = rmp_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY],
            rmp_score = rmp_data[data_keys.PROFESSOR_SCORE_KEY],
            rmp_link = rmp_data[data_keys.PROFESSOR_LINK_KEY]
        )
        supabase.table(TABLE_NAME).update(professor.model_dump())\
            .eq(db_keys.KEY_PROFESSOR_NAME, professor_name)\
            .eq(db_keys.KEY_EMAIL, professor_email)\
            .eq(db_keys.KEY_SCHOOL, school)\
            .eq(db_keys.KEY_DEPARTMENT, department)\
            .execute()

def _add_one_entry(supabase: Client, school: str, department: str, professor_name: str, professor_email: str, rmp_data: dict):
    # new professor added from fetching school data
    professor = Professor(
        professor_name = professor_name,
        email = professor_email,
        school = school,
        department = department,
        rmp_difficulty = rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY],
        rmp_rating = rmp_data[data_keys.PROFESSOR_RATING_KEY],
        rmp_recommend = rmp_data[data_keys.PROFESSOR_RECOMMEND_KEY],
        rmp_reviews_count = rmp_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY],
        rmp_score = rmp_data[data_keys.PROFESSOR_SCORE_KEY],
        rmp_link = rmp_data[data_keys.PROFESSOR_LINK_KEY],
    )
    supabase.table(TABLE_NAME).insert(professor.model_dump()).execute()

def _select_one_query(supabase: Client, school: str, department: str, professor_name: str, professor_email: str) -> Optional[Professor]:
    return supabase.table(TABLE_NAME)\
        .select("*")\
        .eq(db_keys.KEY_PROFESSOR_NAME, professor_name)\
        .eq(db_keys.KEY_EMAIL, professor_email)\
        .eq(db_keys.KEY_SCHOOL, school)\
        .eq(db_keys.KEY_DEPARTMENT, department)\
        .execute()

def should_update(professor_entry: dict) -> bool:
    if db_keys.KEY_UPDATED_AT not in professor_entry:
        return True
    if professor_entry[db_keys.KEY_UPDATED_AT] is None:
        return True
    
    updated_at = datetime.fromisoformat(professor_entry[db_keys.KEY_UPDATED_AT])
    # Make both datetimes naive for comparison
    if updated_at.tzinfo is not None:
        updated_at = updated_at.replace(tzinfo=None)
    return updated_at < datetime.now() - timedelta(days=30)

# TODO: Remove after all data in database is fixed
def get_all(supabase: Client, school: str, department: str) -> dict:
    search_query = supabase.table(TABLE_NAME)\
        .select("*").eq(db_keys.KEY_SCHOOL, school)\
        .eq(db_keys.KEY_DEPARTMENT, department)\
        .execute()
    
    if search_query.data:
        return {professor[db_keys.KEY_PROFESSOR_NAME]: professor for professor in search_query.data}
    else:
        return {}

# TODO: Remove after all data in database is fixed
def update(supabase: Client, professors_data_list: list[dict]):
    logger.info(f"Saving {len(professors_data_list)} professors in database `{TABLE_NAME}`.")
    for professor in professors_data_list:
        # Use all identifying fields to ensure correct row is updated
        supabase.table(TABLE_NAME).update(professor)\
            .eq(db_keys.KEY_PROFESSOR_NAME, professor[db_keys.KEY_PROFESSOR_NAME])\
            .eq(db_keys.KEY_SCHOOL, professor[db_keys.KEY_SCHOOL])\
            .eq(db_keys.KEY_DEPARTMENT, professor[db_keys.KEY_DEPARTMENT])\
            .eq(db_keys.KEY_EMAIL, professor[db_keys.KEY_EMAIL])\
            .execute()