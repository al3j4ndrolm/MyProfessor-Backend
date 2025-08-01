from supabase import Client
from pydantic import BaseModel
from database import db_keys

TABLE_NAME = "courses"

class Course(BaseModel):
    school: str
    data: dict

def save(supabase: Client, courses_data_table: dict, school_name: str):

    courses_data_table = {dept: list(courses) for dept, courses in courses_data_table.items()}
    data = Course(school=school_name, data=courses_data_table)

    # only update if courses already exists for school
    supabase.table(TABLE_NAME).upsert(data.model_dump(), on_conflict=db_keys.COURSES_KEY_SCHOOL).execute()

def get(supabase: Client, school_name: str) -> dict:
    courses = supabase.table(TABLE_NAME).select("*").eq(db_keys.COURSES_KEY_SCHOOL, school_name).execute()
    if len(courses.data) == 0:
        return {}

    return courses.data[0][db_keys.COURSES_KEY_DATA]

