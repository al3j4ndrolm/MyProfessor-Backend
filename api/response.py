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

    school_list = [_create_school(entry, client_data.get("build_type")) for entry in schools_data]
    broadcast_list = [_create_broadcast(entry) for entry in broadcasts_db.get_active(supabase)]

    return {
        configs.SCHOOLS_KEY_SCHOOL_LIST: school_list,
        configs.SCHOOLS_KEY_BROADCASTS: broadcast_list
    }

def response_schools(supabase: Client) -> dict:
    
    school_list = []
    schools_data = schools_db.get(supabase, [SchoolStatus.SUPPORTED])
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

def _create_school(entry: dict, build_type: str) -> dict:
    return {
        configs.SCHOOL_NAME: entry[db_keys.SCHOOL_KEY_SCHOOL_NAME],
        configs.SCHOOL_TERMS: entry[db_keys.SCHOOL_KEY_TERMS],
        configs.SCHOOL_NOTIFICATION: {"text": entry[db_keys.SCHOOL_KEY_NOTIFICATION]},
        configs.SCHOOL_UPDATED_AT: entry[db_keys.KEY_UPDATED_AT],
        configs.SCHOOL_COURSES_UPDATED_AT: entry[db_keys.SCHOOL_KEY_COURSES_UPDATED_AT],
        configs.SCHOOL_FEATURES: _create_school_features(entry[db_keys.SCHOOL_KEY_FEATURES], build_type)
    }

def _create_school_features(database_features: dict, build_type: str) -> {str: bool}:
    if build_type == "dev":
        for key, value in database_features.items():
            database_features[key] = True
        return database_features
    elif build_type == "release":
        return database_features

def _create_school_old(entry: dict) -> dict:
    return {
        configs.SCHOOL_NAME: entry[db_keys.SCHOOL_KEY_SCHOOL_NAME],
        configs.SCHOOL_TERMS: entry[db_keys.SCHOOL_KEY_TERMS],
        configs.SCHOOL_NOTIFICATION: {"text": entry[db_keys.SCHOOL_KEY_NOTIFICATION]},
        "schoolRmpCode": entry[db_keys.SCHOOL_KEY_RMP_CODE],
        configs.SCHOOL_UPDATED_AT: entry[db_keys.KEY_UPDATED_AT],
        configs.SCHOOL_FEATURES: entry[db_keys.SCHOOL_KEY_FEATURES]
    }

def _create_broadcast(entry: dict) -> dict:
    return {
        configs.BROADCAST_ID: entry[db_keys.BROADCAST_KEY_ID],
        configs.BROADCAST_TEXT: entry[db_keys.BROADCAST_KEY_TEXT],
        configs.BROADCAST_MIN_VERSION: entry[db_keys.BROADCAST_KEY_MIN_VERSION],
        configs.BROADCAST_NEED_UPDATE: entry[db_keys.BROADCAST_KEY_MIN_VERSION] is not None,
    }

def _create_broadcast_old(entry: dict) -> dict:
    return {
        configs.BROADCAST_ID: entry[db_keys.BROADCAST_KEY_ID],
        configs.BROADCAST_TEXT: entry[db_keys.BROADCAST_KEY_TEXT],
        configs.BROADCAST_NEED_UPDATE: entry[db_keys.BROADCAST_KEY_MIN_VERSION] is not None,
        configs.BROADCAST_MIN_VERSION: entry[db_keys.BROADCAST_KEY_MIN_VERSION],
    }