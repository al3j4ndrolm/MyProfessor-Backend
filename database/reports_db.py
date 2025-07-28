from supabase import Client
from database import db_keys

TABLE_NAME = "reports"

def save(supabase: Client, body: dict, is_error: bool):
    supabase.table(TABLE_NAME).insert({
        db_keys.REPORTS_KEY_VERSION: body.version,
        db_keys.REPORTS_KEY_RECIPIENT_EMAIL: body.recipient_email,
        db_keys.REPORTS_KEY_CRITICAL: body.critical,
        db_keys.REPORTS_KEY_DETAILS: body.details,
        db_keys.REPORTS_KEY_PLATFORM: body.platform,
        db_keys.REPORTS_KEY_BUILD: body.build,
        db_keys.REPORTS_KEY_IS_ERROR: is_error
    }).execute()