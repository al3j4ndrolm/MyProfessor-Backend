from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from database import db_keys

TABLE_NAME = "classes"

class Classes(BaseModel):
    school: str
    department: str
    term: str
    data: dict
    updated_at: str

def save_one_entry(supabase: Client, data: dict, school: str, term: str, department: str):
    classes = Classes(school=school, department=department, term=term, data=data, updated_at=datetime.now().isoformat())
    search_query = _select_query(supabase, school, term, department)
            
    if not search_query.data:
        supabase.table(TABLE_NAME).insert(classes.model_dump()).execute()
    elif search_query.data[0][db_keys.CLASSES_KEY_DATA] != data:
        _update_one_entry(supabase, classes)

def get_one_entry(supabase: Client, school: str, term: str, department: str) -> dict | None:
    classes = _select_query(supabase, school, term, department)
    if len(classes.data) == 0:
        return {}
    
    class_data = classes.data[0][db_keys.CLASSES_KEY_DATA]
    return class_data

def _select_query(supabase: Client, school: str, term: str, department: str) -> dict:
    return supabase.table(TABLE_NAME)\
        .select("*")\
        .eq(db_keys.CLASSES_KEY_SCHOOL, school)\
        .eq(db_keys.CLASSES_KEY_TERM, term)\
        .eq(db_keys.CLASSES_KEY_DEPARTMENT, department)\
        .execute()

def _update_one_entry(supabase: Client, classes: Classes):
    supabase.table(TABLE_NAME).update(classes.model_dump())\
        .eq(db_keys.CLASSES_KEY_SCHOOL, classes.school)\
        .eq(db_keys.CLASSES_KEY_DEPARTMENT, classes.department)\
        .eq(db_keys.CLASSES_KEY_TERM, classes.term)\
        .execute()

