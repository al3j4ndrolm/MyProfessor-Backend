from supabase import Client
from database import db_keys

TABLE_NAME = "searches"

def save(supabase: Client, school: str, term: str, department: str):
    supabase.table(TABLE_NAME).insert({
        db_keys.SEARCHES_KEY_SCHOOL: school,
        db_keys.SEARCHES_KEY_TERM: term,
        db_keys.SEARCHES_KEY_DEPARTMENT: department
    }).execute()
