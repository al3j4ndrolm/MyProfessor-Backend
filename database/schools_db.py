from supabase import Client
from pydantic import BaseModel
from database import db_keys

TABLE_NAME = "schools"

class School(BaseModel):
    school: str
    rmp_code: str
    terms: list[dict]
    status: int

def save(supabase: Client, school_name: str, rmp_code: str, terms: list[dict]):

    school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=0)
    
    # only update if school already exists
    supabase.table(TABLE_NAME).upsert(school.model_dump(), on_conflict=db_keys.SCHOOL_KEY_SCHOOL_NAME).execute()

def get(supabase: Client) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").execute()
    schools_data = schools.data
    return schools_data
