from supabase import Client

def get(supabase: Client) -> list[dict]:
    broadcasts = supabase.table("broadcasts").select("*").execute()
    broadcasts_data = broadcasts.data
    return broadcasts_data