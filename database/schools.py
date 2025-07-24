from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel

class School(BaseModel):
    school: str
    rmp_code: str
    terms: dict
    status: int

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

schools_table: Client = create_client(url, key).table("schools")

def save_schools_data(school_name: str, rmp_code: str, terms: dict):

    school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=0)
    schools_table.insert(school.model_dump()).execute()

def get_schools_data(supabase: Client) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").execute()
    schools_data = schools.data
    return schools_data