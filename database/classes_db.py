from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel

TABLE_NAME = "classes"

class Classes(BaseModel):
    school: str
    department: str
    term: str
    data: dict

def save(supabase: Client, classes_data_table: dict, school: str):
    for term, classes_all_departments in classes_data_table.items():
        for department, classes_per_department in classes_all_departments.items():
            
            classes = Classes(school=school, department=department, term=term, data=classes_per_department)
            supabase.table(TABLE_NAME).insert(classes.model_dump()).execute()

def get(supabase: Client, school: str, term: str, department: str) -> dict:
    classes = supabase.table(TABLE_NAME).select("*").eq("school", school).eq("term", term).eq("department", department).execute()
    if len(classes.data) == 0:
        return {}
    
    class_data = classes.data[0]["data"]
    return class_data

