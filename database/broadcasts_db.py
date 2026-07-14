from supabase import Client
from database import db_keys

TABLE_NAME = "broadcasts"

def get_active(supabase: Client) -> list[dict]:
    broadcasts = supabase.table(TABLE_NAME).select("*").eq(db_keys.BROADCAST_KEY_ACTIVE, True).execute()
    broadcasts_data = broadcasts.data
    return broadcasts_data