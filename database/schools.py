from supabase import Client
from pydantic import BaseModel

TABLE_NAME = "schools"

class School(BaseModel):
    school: str
    rmp_code: str
    terms: dict
    status: int

def save_schools_data(supabase: Client, school_name: str, rmp_code: str, terms: dict):

    school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=0)
    
    supabase.table(TABLE_NAME).insert(school.model_dump()).execute()

