from supabase import Client

from database.schools import get_schools_data
from data_fetchers.api.schools.configs import SCHOOL_NAME_KEY, RMP_CODE_KEY, TERMS_KEY, NOTIFICATION_KEY, STATUS_KEY

def create_schools_data(supabase: Client) -> dict:
    schools_data = get_schools_data(supabase)

    school_list = []
    for entry in schools_data:
        school_list.append(create_school_list(entry))

    return {"schools": school_list, "broadcasts": []}

def create_school_list(entry: dict) -> dict:
    return {
        SCHOOL_NAME_KEY: entry["school"],
        RMP_CODE_KEY: entry["rmp_code"],
        TERMS_KEY: entry["terms"],
        NOTIFICATION_KEY: {"text": entry["notification"]},
        STATUS_KEY: entry["status"]
    }