from supabase import Client
from pydantic import BaseModel
from data_fetchers.api.schools.response import create_schools_data

TABLE_NAME = "schools"

class School(BaseModel):
    school: str
    rmp_code: str
    terms: list[dict]
    status: int

def save_schools_data(supabase: Client, school_name: str, rmp_code: str, terms: list[dict]):

    school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=0)
    
    supabase.table(TABLE_NAME).insert(school.model_dump()).execute()

def get_schools_data(supabase: Client) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").execute()
    schools_data = schools.data
    return create_schools_data(schools_data)