from supabase import Client

from database import schools_db, broadcasts_db
from api import configs

def response_schools(supabase: Client) -> dict:
    schools_data = schools_db.get(supabase)
    broadcasts_data = broadcasts_db.get(supabase)
    school_list = []
    broadcast_list = []

    for entry in schools_data:
        school_list.append(_create_school_list(entry))
    for entry in broadcasts_data:
        broadcast_list.append(_create_broadcast_list(entry))

    return {"schools": school_list, "broadcasts": broadcast_list}

def _create_school_list(entry: dict) -> dict:
    return {
        configs.SCHOOL_NAME_KEY: entry["school"],
        configs.RMP_CODE_KEY: entry["rmp_code"],
        configs.TERMS_KEY: entry["terms"],
        configs.NOTIFICATION_KEY: {"text": entry["notification"]},
        configs.STATUS_KEY: entry["status"]
    }

def _create_broadcast_list(entry: dict) -> dict:

    return {
        configs.BROADCAST_ID_KEY: entry["id"],
        configs.TEXT_KEY: entry["text"],
        configs.NEED_UPDATE_KEY: entry["need_update"],
        configs.MIN_VERSION_KEY: entry["min_version"],
        configs.PLATFORM_KEY: entry["platform"]
    }
