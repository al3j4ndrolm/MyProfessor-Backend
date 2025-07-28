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
    select_query = supabase.table(TABLE_NAME).select("*").eq(db_keys.SCHOOL_KEY_SCHOOL_NAME, school_name).execute()
    if select_query.data:
        school = select_query.data[0]
        school.status = SchoolStatus.READY.value
        school.rmp_code = rmp_code
        school.terms = terms
    else:
        school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=SchoolStatus.READY.value, notification="")

    # only update if school already exists
    supabase.table(TABLE_NAME).upsert(school.model_dump(), on_conflict=db_keys.SCHOOL_KEY_SCHOOL_NAME).execute()

def set_status(supabase: Client, school_name: str, status: int):
    supabase.table(TABLE_NAME).update({db_keys.SCHOOL_KEY_STATUS: status})\
        .eq(db_keys.SCHOOL_KEY_SCHOOL_NAME, school_name).execute()

def get_supported(supabase: Client) -> list[dict]:
    return get(supabase, status=SchoolStatus.SUPPORTED.value)

def get(supabase: Client, status: int) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").eq(db_keys.SCHOOL_KEY_STATUS, status).execute()
    schools_data = schools.data
    return schools_data
