from deprecation import deprecated
from supabase import Client

from database import schools_db, broadcasts_db, professors_db, classes_db, db_keys
from api import configs
from helpers.data import data_keys

def response_start(supabase: Client) -> dict:
    
    school_list = []
    schools_data = schools_db.get_supported(supabase)
    for entry in schools_data:
        school_list.append(_create_school(entry))
    
    broadcast_list = []
    broadcasts_data = broadcasts_db.get(supabase)
    for entry in broadcasts_data:
        broadcast_list.append(_create_broadcast(entry))

    return {
        configs.SCHOOLS_KEY_SCHOOL_LIST: school_list,
        configs.SCHOOLS_KEY_BROADCASTS: broadcast_list
    }

def response_schools(supabase: Client) -> dict:
    
    school_list = []
    schools_data = schools_db.get_supported(supabase)
    for entry in schools_data:
        school_list.append(_create_school(entry))
    
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
        configs.RMP_CODE_KEY: entry[db_keys.SCHOOL_KEY_RMP_CODE],
        configs.TERMS_KEY: entry[db_keys.SCHOOL_KEY_TERMS],
        configs.NOTIFICATION_KEY: {"text": entry[db_keys.SCHOOL_KEY_NOTIFICATION]},
        configs.STATUS_KEY: entry[db_keys.SCHOOL_KEY_STATUS]
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

def _create_my_collection_sync_response(entry: dict) -> dict:
    return {
        configs.MY_COLLECTION_SYNC_KEY_SCHOOL: entry[db_keys.MY_COLLECTION_SYNC_KEY_SCHOOL],
        configs.MY_COLLECTION_SYNC_KEY_TERM: entry[db_keys.MY_COLLECTION_SYNC_KEY_TERM],
        configs.MY_COLLECTION_SYNC_KEY_DEPARTMENT: entry[db_keys.MY_COLLECTION_SYNC_KEY_DEPARTMENT],
        configs.MY_COLLECTION_SYNC_KEY_PROFESSOR_NAME: entry[db_keys.MY_COLLECTION_SYNC_KEY_PROFESSOR_NAME],
        configs.MY_COLLECTION_SYNC_KEY_PROFESSOR_EMAIL: entry[db_keys.MY_COLLECTION_SYNC_KEY_PROFESSOR_EMAIL],
        configs.MY_COLLECTION_SYNC_KEY_COURSE_CODE: entry[db_keys.MY_COLLECTION_SYNC_KEY_COURSE_CODE],
        configs.MY_COLLECTION_SYNC_KEY_CLASSES: entry[db_keys.MY_COLLECTION_SYNC_KEY_CLASSES],
    }