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
    ai_summary: Optional[dict] = None

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

def get_unique_rmp_links(supabase: Client, school: str) -> list[str]:
    search_query = supabase.table(TABLE_NAME)\
        .select(db_keys.KEY_RMP_LINK)\
        .eq(db_keys.KEY_SCHOOL, school)\
        .execute()

    rmp_links = set()
    for professor in search_query.data:
        if professor[db_keys.KEY_RMP_LINK] is not None:
            rmp_links.add(professor[db_keys.KEY_RMP_LINK])

    return list(rmp_links)

def get_unique_rmp_links_without_summary(supabase: Client, school: str) -> list[str]:
    """
    Get unique RMP links from professors table whose ai_summary field is not yet set.
    """
    # Get RMP link and ai_summary for every professor with a non-null RMP link
    professors_response = supabase.table(TABLE_NAME)\
        .select(f"{db_keys.KEY_RMP_LINK},{db_keys.KEY_AI_SUMMARY}")\
        .eq(db_keys.KEY_SCHOOL, school)\
        .not_.is_(db_keys.KEY_RMP_LINK, "null")\
        .execute()

    # Keep links for professors that don't have an ai_summary yet
    unique_links = set()
    for professor in professors_response.data:
        rmp_link = professor[db_keys.KEY_RMP_LINK]
        ai_summary = professor[db_keys.KEY_AI_SUMMARY]
        if rmp_link and not ai_summary:
            unique_links.add(rmp_link)
    
    return list(unique_links)

def update_ai_summary(supabase: Client, rmp_link: str, ai_summary: dict):
    """
    Find all professor entries matching the given rmp_link and update their ai_summary.
    """
    supabase.table(TABLE_NAME)\
        .update({db_keys.KEY_AI_SUMMARY: ai_summary})\
        .eq(db_keys.KEY_RMP_LINK, rmp_link)\
        .execute()
