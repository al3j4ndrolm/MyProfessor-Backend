from supabase import Client
from database import db_keys

TABLE_NAME = "reports"

def save(supabase: Client, crash_report: dict, is_error: bool):
    supabase.table(TABLE_NAME).insert({
        db_keys.REPORTS_KEY_VERSION: crash_report.version,
        db_keys.REPORTS_KEY_CRITICAL: crash_report.critical,
        db_keys.REPORTS_KEY_DETAILS: crash_report.details,
        db_keys.REPORTS_KEY_PLATFORM: crash_report.platform,
        db_keys.REPORTS_KEY_BUILD: crash_report.build,
        db_keys.REPORTS_KEY_IS_ERROR: is_error
    }).execute()

def save(supabase: Client, build: str, platform: str, data: dict):
    supabase.table(TABLE_NAME).insert({
        db_keys.REPORTS_KEY_VERSION: None,
        db_keys.REPORTS_KEY_CRITICAL: False,
        db_keys.REPORTS_KEY_DETAILS: str(data),
        db_keys.REPORTS_KEY_PLATFORM: platform,
        db_keys.REPORTS_KEY_BUILD: build,
        db_keys.REPORTS_KEY_IS_ERROR: False
    }).execute()