from deprecation import deprecated
from supabase import Client
from pydantic import BaseModel
from typing import Optional
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
    rmp_recommend: Optional[float] = None
    rmp_reviews_count: Optional[int] = None
    rmp_score: Optional[float] = None
    rmp_link: Optional[str] = None

def get(supabase: Client, school: str, department: str, professor_name: str, professor_email: str) -> Optional[Professor]:
    search_query = supabase.table(TABLE_NAME)\
        .select("*").eq(db_keys.KEY_PROFESSOR_NAME, professor_name)\
        .eq(db_keys.KEY_EMAIL, professor_email)\
        .eq(db_keys.KEY_SCHOOL, school)\
        .eq(db_keys.KEY_DEPARTMENT, department)\
        .execute()
    
    return search_query.data[0] if search_query.data else None

def get_all(supabase: Client, school: str, department: str) -> dict:
    search_query = supabase.table(TABLE_NAME)\
        .select("*").eq(db_keys.KEY_SCHOOL, school)\
        .eq(db_keys.KEY_DEPARTMENT, department)\
        .execute()
    
    if search_query.data:
        return {professor[db_keys.KEY_PROFESSOR_NAME]: professor for professor in search_query.data}
    else:
        return {}

def save(supabase: Client, professors_data_table: dict, school: str, department: str):
    to_insert = []

    for professor_tuple, professor_data in professors_data_table.items():
        # only insert if professor does not exist
        professor_name, professor_email = professor_tuple
        search_query = supabase.table(TABLE_NAME)\
            .select("*").eq(db_keys.KEY_PROFESSOR_NAME, professor_name)\
            .eq(db_keys.KEY_EMAIL, professor_email)\
            .eq(db_keys.KEY_SCHOOL, school)\
            .eq(db_keys.KEY_DEPARTMENT, department)\
            .execute()
        
        if not search_query.data:
            # new professor added from fetching school data
            professor = Professor(
                professor_name = professor_name,
                email = professor_email,
                school = school,
                department = department,
                rmp_difficulty = professor_data[data_keys.PROFESSOR_DIFFICULTY_KEY],
                rmp_rating = professor_data[data_keys.PROFESSOR_RATING_KEY],
                rmp_recommend = professor_data[data_keys.PROFESSOR_RECOMMEND_KEY],
                rmp_reviews_count = professor_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY],
                rmp_score = professor_data[data_keys.PROFESSOR_SCORE_KEY],
                rmp_link = professor_data[data_keys.PROFESSOR_LINK_KEY]) 
            to_insert.append(professor.model_dump())

    # insert all professors at once
    supabase.table(TABLE_NAME).insert(to_insert).execute()

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

# TODO: Remove after client migrates to new classes endpoints
def get_without_email(supabase: Client, school: str, department: str, professor_name: str) -> Optional[Professor]:
    search_query = supabase.table(TABLE_NAME)\
        .select("*").eq(db_keys.KEY_PROFESSOR_NAME, professor_name)\
        .eq(db_keys.KEY_SCHOOL, school)\
        .eq(db_keys.KEY_DEPARTMENT, department)\
        .execute()
    
    return search_query.data[0] if search_query.data else None