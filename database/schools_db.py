from supabase import Client
from pydantic import BaseModel
from enum import IntEnum
from database import db_keys

TABLE_NAME = "schools"

class SchoolStatus(IntEnum):
    UNKNOWN = 0
    READY = 1
    SUPPORTED = 2
    MAINTENANCE = 3

class School(BaseModel):
    school: str
    rmp_code: str
    terms: list[dict]
    status: int
    notification: str

def save(supabase: Client, school_name: str, rmp_code: str, terms: list[dict]):

    school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=SchoolStatus.READY.value, notification="")
    
    select_query = supabase.table(TABLE_NAME).select("*").eq(db_keys.SCHOOL_KEY_SCHOOL_NAME, school_name).execute()
    if select_query.data:
        school.status = select_query.data[0][db_keys.SCHOOL_KEY_STATUS]
        school.notification = select_query.data[0][db_keys.SCHOOL_KEY_NOTIFICATION]

    # only update if school already exists
    supabase.table(TABLE_NAME).upsert(school.model_dump(), on_conflict=db_keys.SCHOOL_KEY_SCHOOL_NAME).execute()

def get_supported(supabase: Client) -> list[dict]:
    return _get(supabase, status=SchoolStatus.SUPPORTED.value)

def _get(supabase: Client, status: int) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").eq(db_keys.SCHOOL_KEY_STATUS, status).execute()
    schools_data = schools.data
    return schools_data
