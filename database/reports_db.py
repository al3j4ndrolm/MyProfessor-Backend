from supabase import Client
from database import db_keys

TABLE_NAME = "reports"

def save(supabase: Client, build: str, platform: str, data: dict):
    supabase.table(TABLE_NAME).insert({
        db_keys.REPORTS_KEY_VERSION: None,
        db_keys.REPORTS_KEY_CRITICAL: False,
        db_keys.REPORTS_KEY_DETAILS: str(data),
        db_keys.REPORTS_KEY_PLATFORM: platform,
        db_keys.REPORTS_KEY_BUILD: build,
        db_keys.REPORTS_KEY_IS_ERROR: False
    }).execute()

def save_error(supabase: Client, version: str, critical: bool, details: str, platform: str, build: str):
    supabase.table(TABLE_NAME).insert({
        db_keys.REPORTS_KEY_VERSION: version,
        db_keys.REPORTS_KEY_CRITICAL: critical,
        db_keys.REPORTS_KEY_DETAILS: details,
        db_keys.REPORTS_KEY_PLATFORM: platform,
        db_keys.REPORTS_KEY_BUILD: build,
        db_keys.REPORTS_KEY_IS_ERROR: True
    }).execute()
