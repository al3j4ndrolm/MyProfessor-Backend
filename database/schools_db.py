from supabase import Client
from pydantic import BaseModel
from enum import IntEnum
from database import db_keys

TABLE_NAME = "schools"

class SchoolStatus(IntEnum):
    FETCHING = 0
    READY = 1
    SUPPORTED = 2
    MAINTENANCE = 3
    TESTING = 4

class School(BaseModel):
    school: str
    rmp_code: str
    terms: list[dict]
    status: int
    notification: str

def save(supabase: Client, school_name: str, rmp_code: str, terms: list[dict]):
    select_query = supabase.table(TABLE_NAME).select("*").eq(db_keys.SCHOOL_KEY_SCHOOL_NAME, school_name).execute()
    if select_query.data:
        school_entry = select_query.data[0]
        school_entry[db_keys.SCHOOL_KEY_STATUS] = SchoolStatus.FETCHING.value
        school_entry[db_keys.SCHOOL_KEY_RMP_CODE] = rmp_code
        school_entry[db_keys.SCHOOL_KEY_TERMS] = terms
        supabase.table(TABLE_NAME).update(school_entry).eq(db_keys.SCHOOL_KEY_SCHOOL_NAME, school_name).execute()
    else:
        school = School(school=school_name, rmp_code=rmp_code, terms=terms, status=SchoolStatus.FETCHING.value, notification="")
        supabase.table(TABLE_NAME).upsert(school.model_dump(), on_conflict=db_keys.SCHOOL_KEY_SCHOOL_NAME).execute()

def set_status(supabase: Client, school_name: str, status: int):
    supabase.table(TABLE_NAME).update({db_keys.SCHOOL_KEY_STATUS: status})\
        .eq(db_keys.SCHOOL_KEY_SCHOOL_NAME, school_name).execute()

def get(supabase: Client, statuses: list[SchoolStatus]) -> list[dict]:
    schools = supabase.table(TABLE_NAME).select("*").in_(db_keys.SCHOOL_KEY_STATUS, statuses).execute()
    schools_data = schools.data
    return schools_data
