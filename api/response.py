from deprecation import deprecated
from supabase import Client

from database import schools_db, broadcasts_db, professors_db, classes_db, db_keys
from api import configs
from helpers.data import data_keys

def response_schools(supabase: Client) -> dict:
    schools_data = schools_db.get(supabase)
    broadcasts_data = broadcasts_db.get(supabase)
    school_list = []
    broadcast_list = []

    for entry in schools_data:
        school_list.append(_create_school_list(entry))
    for entry in broadcasts_data:
        broadcast_list.append(_create_broadcast_list(entry))

    return {
        configs.SCHOOLS_KEY_SCHOOL_LIST: school_list,
        configs.SCHOOLS_KEY_BROADCASTS: broadcast_list
    }

def _create_school_list(entry: dict) -> dict:
    return {
        configs.SCHOOL_NAME_KEY: entry[db_keys.SCHOOL_KEY_SCHOOL_NAME],
        configs.RMP_CODE_KEY: entry[db_keys.SCHOOL_KEY_RMP_CODE],
        configs.TERMS_KEY: entry[db_keys.SCHOOL_KEY_TERMS],
        configs.NOTIFICATION_KEY: {"text": entry[db_keys.SCHOOL_KEY_NOTIFICATION]},
        configs.STATUS_KEY: entry[db_keys.SCHOOL_KEY_STATUS]
    }

def _create_broadcast_list(entry: dict) -> dict:
    return {
        configs.BROADCAST_ID_KEY: entry[db_keys.BROADCAST_KEY_ID],
        configs.TEXT_KEY: entry[db_keys.BROADCAST_KEY_TEXT],
        configs.NEED_UPDATE_KEY: entry[db_keys.BROADCAST_KEY_NEED_UPDATE],
        configs.MIN_VERSION_KEY: entry[db_keys.BROADCAST_KEY_MIN_VERSION],
        configs.PLATFORM_KEY: entry[db_keys.BROADCAST_KEY_PLATFORM]
    }

def response_classes(supabase: Client, school: str, term: str, department: str) -> dict:
    classes_all_courses = classes_db.get(supabase, school, term, department)

    for course, classes_all_professors in classes_all_courses.items():
        for professor_name, professor_data in classes_all_professors.items():
            professor_email = professor_data[data_keys.EMAIL_KEY]
            
            # TODO: instead of getting single professor, get all from the same school and department
            professor_entry = professors_db.get(supabase, school, department, professor_name, professor_email)
            if professor_entry:
                professor_data[data_keys.RATING_KEY] = professor_entry[db_keys.PROFESSOR_KEY_RMP_RATING]
                professor_data[data_keys.DIFFICULTY_KEY] = professor_entry[db_keys.PROFESSOR_KEY_RMP_DIFFICULTY]
                professor_data[data_keys.RECOMMEND_KEY] = professor_entry[db_keys.PROFESSOR_KEY_RMP_RECOMMEND]
                professor_data[data_keys.REVIEW_COUNT_KEY] = professor_entry[db_keys.PROFESSOR_KEY_RMP_REVIEWS_COUNT]
            if not professor_data[data_keys.RATING_KEY]:
                professor_data[data_keys.RATING_KEY] = -0.1
            if not professor_data[data_keys.DIFFICULTY_KEY]:
                professor_data[data_keys.DIFFICULTY_KEY] = 5.1
            if not professor_data[data_keys.RECOMMEND_KEY]:
                professor_data[data_keys.RECOMMEND_KEY] = -1
            if not professor_data[data_keys.REVIEW_COUNT_KEY]:
                professor_data[data_keys.REVIEW_COUNT_KEY] = 0
            del professor_data[data_keys.EMAIL_KEY]

    return classes_all_courses
