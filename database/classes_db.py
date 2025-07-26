from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from database import db_keys

TABLE_NAME = "classes"

class Classes(BaseModel):
    school: str
    department: str
    term: str
    data: dict

def save(supabase: Client, classes_data_table: dict, school: str):
    to_insert = []
    to_update = []

    for term, classes_all_departments in classes_data_table.items():
        for department, classes_per_department in classes_all_departments.items():
            classes = Classes(school=school, department=department, term=term, data=classes_per_department)
           
            search_query = _select_query(supabase, school, term, department)
            
            if not search_query.data:
                to_insert.append(classes.model_dump())
            elif search_query.data[0][db_keys.CLASSES_KEY_DATA] != classes.model_dump():
                to_update.append(classes.model_dump())

    if to_insert:
        supabase.table(TABLE_NAME).insert(to_insert).execute()
    if to_update:
        _update_batch(supabase, to_update)

def get(supabase: Client, school: str, term: str, department: str) -> dict:
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

def _update_batch(supabase: Client, to_update: list[dict]):
    for row in to_update:
        supabase.table(TABLE_NAME).update(row)\
            .eq(db_keys.CLASSES_KEY_SCHOOL, row[db_keys.CLASSES_KEY_SCHOOL])\
            .eq(db_keys.CLASSES_KEY_DEPARTMENT, row[db_keys.CLASSES_KEY_DEPARTMENT])\
            .eq(db_keys.CLASSES_KEY_TERM, row[db_keys.CLASSES_KEY_TERM])\
            .execute()
