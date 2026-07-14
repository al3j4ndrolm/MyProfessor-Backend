import time, requests
from supabase import Client
from logger import logger

from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.school_data.sfsu.school_config import SCHEDULES_BASE_URL, SCHEDULES_RESULT_JSON_URL, SCHOOL_NAME, RMP_CODE, TERMS_BASE_URL
from data_fetchers.school_data.sfsu.terms import get_terms
from data_fetchers.school_data.sfsu.departments import get_department_data_table
from data_fetchers.school_data.sfsu.courses import update_courses_set_per_term
from data_fetchers.school_data.sfsu.schedules import get_classes_per_department
from data_fetchers.school_data.common.pipeline import run_school_fetch

def main(supabase: Client, target_tables: set[str]) -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(soup)
    term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

    def get_courses_and_classes_lazy() -> tuple[dict, dict]:
        departments = sorted(list(get_department_data_table(soup).keys()))
        return get_courses_and_classes(departments, term_codes)

    run_school_fetch(supabase, target_tables, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)

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