from supabase import Client
from pydantic import BaseModel

TABLE_NAME = "schools"

class School(BaseModel):
    school: str
    rmp_code: str
    terms: list[dict]
    status: int

def save(supabase: Client, school_name: str, rmp_code: str, terms: list[dict]):

    school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=0)
    
    # Check if school already exists
    existing_school = supabase.table(TABLE_NAME).select("*").eq("school", school_name).execute()
    
    if existing_school.data:
        # Update existing school
        supabase.table(TABLE_NAME).update(school.model_dump()).eq("school", school_name).execute()
    else:
        # Insert new school
        supabase.table(TABLE_NAME).insert(school.model_dump()).execute()

def get(supabase: Client) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").execute()
    schools_data = schools.data
    return schools_data
