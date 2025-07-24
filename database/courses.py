from supabase import Client
from pydantic import BaseModel

TABLE_NAME = "courses"

class Course(BaseModel):
    school: str
    data: dict

def save_courses_data(supabase: Client, courses_data_table: dict, school_name: str):

    courses_data_table = {dept: list(courses) for dept, courses in courses_data_table.items()}
    data = Course(school=school_name, data=courses_data_table)
    
    supabase.table(TABLE_NAME).insert(data.model_dump()).execute()
