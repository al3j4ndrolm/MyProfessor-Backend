from supabase import Client
from database import db_keys

TABLE_NAME = "broadcasts"

def get(supabase: Client) -> list[dict]:
    broadcasts = supabase.table(TABLE_NAME).select("*").execute()
    broadcasts_data = broadcasts.data
    return broadcasts_data