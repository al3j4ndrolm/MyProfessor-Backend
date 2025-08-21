from supabase import Client
from pydantic import BaseModel
from typing import Optional
from database import db_keys

TABLE_NAME = "summaries"

class Summary(BaseModel):
    rmp_link: str
    summary: Optional[dict] = None

def get_one_entry(supabase: Client, rmp_link: str) -> Optional[Summary]:
    response = supabase.table(TABLE_NAME).select("*").eq(db_keys.SUMMARIES_KEY_RMP_LINK, rmp_link).execute()
    if response.data:
        return response.data[0]
    else:
        return None

def save_one_entry(supabase: Client, rmp_link: str, summary: dict):
    supabase.table(TABLE_NAME).upsert({
        db_keys.SUMMARIES_KEY_RMP_LINK: rmp_link, 
        db_keys.SUMMARIES_KEY_SUMMARY: summary
    }).execute()