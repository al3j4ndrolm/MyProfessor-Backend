import time, requests
from supabase import Client
from logger import logger

from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.schools.sfsu.school_config import SCHEDULES_BASE_URL, SCHEDULES_RESULT_JSON_URL, SCHOOL_NAME, RMP_CODE, TERMS_BASE_URL
from data_fetchers.schools.sfsu.terms import get_terms
from data_fetchers.schools.sfsu.departments import get_department_data_table
from data_fetchers.schools.sfsu.courses import update_courses_set_per_term
from data_fetchers.schools.sfsu.schedules import get_classes_per_department
from data_fetchers.ratings.rating_provider import get_ratings_and_merge
from database import courses_db, schools_db, classes_db
from database.schools_db import SchoolStatus

def main(supabase: Client, target_tables: set[str]) -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(soup)
    if "schools" in target_tables:
        logger.info("Saving school data to database `schools`.")
        schools_db.save(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list)

    if "courses" in target_tables or "classes" in target_tables:
        departments = sorted(list(get_department_data_table(soup).keys()))
        term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]
        courses_data_table, classes_data_table = get_courses_and_classes(departments, term_codes)

        if "courses" in target_tables:
            logger.info("Saving courses data to database `courses`.")
            courses_db.save(supabase, courses_data_table, SCHOOL_NAME)

        if "classes" in target_tables:
            logger.info("Merging ratings data to classes data ...")
            for term_code, classes_all_departments in classes_data_table.items():
                for department_code, classes_one_department in classes_all_departments.items():
                    get_ratings_and_merge(supabase, classes_one_department, SCHOOL_NAME, RMP_CODE, department_code)
                    logger.info(f"Saving classes data for {department_code} in term {term_code} to database `classes`.")
                    classes_db.save_one_entry(supabase, classes_one_department, SCHOOL_NAME, term_code, department_code)

    logger.info(f"Completed fetching. Setting {SCHOOL_NAME} status to `supported`.")
    schools_db.set_status(supabase, SCHOOL_NAME, SchoolStatus.READY.value)

def get_courses_and_classes(departments: list, term_codes: list) -> tuple[dict, dict]:
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for department_code in departments:

        courses = set()
        for term_code in term_codes:
            session_data = get_session_data(department_code, term_code)

            logger.debug(f"Getting schedules for {department_code} in {term_code} ...")
            department_schedules = get_classes_per_department(session_data, department_code)
            classes_data_table[term_code][department_code.replace(" ", "")] = department_schedules

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            update_courses_set_per_term(session_data, courses, department_code)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code.replace(" ", "")] = courses

    return courses_data_table, classes_data_table

def get_session_data(department_code: str, term_code: str):
    try:
        session = requests.Session()
        # 1) prime your session with the filters
        session.get(
            SCHEDULES_BASE_URL,
            params={
                "searchFor":     department_code,   # ← your department code
                "term":          term_code,
                "classCategory": "REG",
            }
        )
        # 2) now fetch the JSON (timestamp only matters to bust cache)
        r = session.get(
            SCHEDULES_RESULT_JSON_URL,
            params={"_": int(time.time() * 1000)}
        )
        data = r.json()
        return data
    except Exception as e:
        logger.error(f"Error getting data for {department_code} set per term {term_code}: {e}")
        return {}