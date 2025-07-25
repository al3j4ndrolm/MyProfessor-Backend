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
    to_insert = []
    to_update = []

    for term, classes_all_departments in classes_data_table.items():
        for department, classes_per_department in classes_all_departments.items():
            classes = Classes(school=school, department=department, term=term, data=classes_per_department)
            search_query = supabase.table(TABLE_NAME).select("*").eq("school", school).eq("department", department).eq("term", term).execute()
            
            if not search_query.data:
                to_insert.append(classes.model_dump())
            elif search_query.data[0]["data"] != classes.model_dump():
                to_update.append(classes.model_dump())

    if to_insert:
        supabase.table(TABLE_NAME).insert(to_insert).execute()
    if to_update:
        for row in to_update:
            supabase.table(TABLE_NAME).update(row)\
                .eq("school", row["school"])\
                .eq("department", row["department"])\
                .eq("term", row["term"])\
                .execute()

def get(supabase: Client, school: str, term: str, department: str) -> dict:
    classes = supabase.table(TABLE_NAME).select("*").eq("school", school).eq("term", term).eq("department", department).execute()
    if len(classes.data) == 0:
        return {}
    
    class_data = classes.data[0]["data"]
    return class_data

