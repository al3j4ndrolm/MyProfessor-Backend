from storage3._sync import client
from supabase import Client

from database import schools_db, broadcasts_db, db_keys
from database.schools_db import SchoolStatus
from api import configs

def response_start(supabase: Client, client_data: dict, user_data: dict) -> dict:
    

    if client_data.get("build_type") == "dev":
        schools_data = schools_db.get(supabase, [SchoolStatus.SUPPORTED, SchoolStatus.TESTING])
    elif client_data.get("build_type") == "release":
        schools_data = schools_db.get(supabase, [SchoolStatus.SUPPORTED])
    else:
        schools_data = schools_db.get(supabase, [])

    school_list = [_create_school(entry) for entry in schools_data]
    broadcast_list = [_create_broadcast(entry) for entry in broadcasts_db.get_active(supabase)]

    return {
        configs.SCHOOLS_KEY_SCHOOL_LIST: school_list,
        configs.SCHOOLS_KEY_BROADCASTS: broadcast_list
    }

def response_schools(supabase: Client) -> dict:
    
    school_list = []
    schools_data = schools_db.get_supported(supabase)
    for entry in schools_data:
        school_list.append(_create_school_old(entry))
    
    broadcast_list = []
    broadcasts_data = broadcasts_db.get(supabase)
    for entry in broadcasts_data:
        broadcast_list.append(_create_broadcast_old(entry))

    return {
        configs.SCHOOLS_KEY_SCHOOL_LIST: school_list,
        configs.SCHOOLS_KEY_BROADCASTS: broadcast_list
    }

def _create_school(entry: dict) -> dict:
    return {
        configs.SCHOOL_NAME_KEY: entry[db_keys.SCHOOL_KEY_SCHOOL_NAME],
        configs.TERMS_KEY: entry[db_keys.SCHOOL_KEY_TERMS],
        configs.NOTIFICATION_KEY: {"text": entry[db_keys.SCHOOL_KEY_NOTIFICATION]},
        configs.KEY_UPDATED_AT: entry[db_keys.KEY_UPDATED_AT]
    }

def _create_school_old(entry: dict) -> dict:
    return {
        configs.SCHOOL_NAME_KEY: entry[db_keys.SCHOOL_KEY_SCHOOL_NAME],
        configs.TERMS_KEY: entry[db_keys.SCHOOL_KEY_TERMS],
        configs.NOTIFICATION_KEY: {"text": entry[db_keys.SCHOOL_KEY_NOTIFICATION]},
        "schoolRmpCode": entry[db_keys.SCHOOL_KEY_RMP_CODE],
        configs.KEY_UPDATED_AT: entry[db_keys.KEY_UPDATED_AT]
    }

def _create_broadcast(entry: dict) -> dict:
    return {
        configs.BROADCAST_ID_KEY: entry[db_keys.BROADCAST_KEY_ID],
        configs.BROADCAST_TEXT_KEY: entry[db_keys.BROADCAST_KEY_TEXT],
        configs.BROADCAST_MIN_VERSION_KEY: entry[db_keys.BROADCAST_KEY_MIN_VERSION],
    }

def _create_broadcast_old(entry: dict) -> dict:
    return {
        configs.BROADCAST_ID_KEY: entry[db_keys.BROADCAST_KEY_ID],
        configs.BROADCAST_TEXT_KEY: entry[db_keys.BROADCAST_KEY_TEXT],
        configs.BROADCAST_NEED_UPDATE_KEY: entry[db_keys.BROADCAST_KEY_MIN_VERSION] is not None,
        configs.BROADCAST_MIN_VERSION_KEY: entry[db_keys.BROADCAST_KEY_MIN_VERSION],
    }