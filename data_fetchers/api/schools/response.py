from supabase import Client

from database.schools import get_schools_data
from database.broadcasts import get_broadcasts_data
from data_fetchers.api.schools.configs import SCHOOL_NAME_KEY, RMP_CODE_KEY, TERMS_KEY, NOTIFICATION_KEY, STATUS_KEY, TEXT_KEY, NEED_UPDATE_KEY, MIN_VERSION_KEY, PLATFORM_KEY, BROADCAST_ID_KEY

def create_schools_response(supabase: Client) -> dict:
    schools_data = get_schools_data(supabase)
    broadcasts_data = get_broadcasts_data(supabase)
    school_list = []
    broadcast_list = []

    for entry in schools_data:
        school_list.append(create_school_list(entry))
    for entry in broadcasts_data:
        broadcast_list.append(create_broadcast_list(entry))

    return {"schools": school_list, "broadcasts": broadcast_list}

def create_school_list(entry: dict) -> dict:
    return {
        SCHOOL_NAME_KEY: entry["school"],
        RMP_CODE_KEY: entry["rmp_code"],
        TERMS_KEY: entry["terms"],
        NOTIFICATION_KEY: {"text": entry["notification"]},
        STATUS_KEY: entry["status"]
    }

def create_broadcast_list(entry: dict) -> dict:

    return {
        BROADCAST_ID_KEY: entry["id"],
        TEXT_KEY: entry["text"],
        NEED_UPDATE_KEY: entry["need_update"],
        MIN_VERSION_KEY: entry["min_version"],
        PLATFORM_KEY: entry["platform"]
    }