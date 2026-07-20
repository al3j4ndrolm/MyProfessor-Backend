# Standard library imports
import time
from supabase import Client

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.school_data.schools.ccsf.terms import get_terms
from data_fetchers.school_data.schools.ccsf.courses import update_courses_data_table
from data_fetchers.school_data.schools.ccsf.schedules import get_classes_per_department
from data_fetchers.school_data.schools.ccsf.departments import get_department_data_table
from data_fetchers.school_data.schools.ccsf.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.school_data.common.pipeline import run_school_fetch
from logger import logger

def main(supabase: Client) -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(soup)
    term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

    def get_courses_and_classes_lazy() -> tuple[dict, dict]:
        department_data_table = get_department_data_table(soup)
        return get_courses_and_classes(department_data_table, term_codes)

    run_school_fetch(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)

def get_courses_and_classes(department_data_table: dict, term_codes: list) -> tuple[dict, dict]:
    """
    Get the courses and classes from the soup.
    """
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for department_code, department_full_name in department_data_table.items():
        courses = set()
        for term_code in term_codes:

            department_url = _get_department_url(department_code, term_code)
            department_soup = html_url_to_soup(department_url)

            logger.debug(f"Getting classes for {department_code} in {term_code} ...")
            classes_per_department = get_classes_per_department(department_soup, department_code)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            update_courses_data_table(department_soup, courses_data_table, department_code)

            time.sleep(1)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table

def _get_department_url(department_code: str, term_code: str) -> str:
    # TODO: Modify this based on your school's url structure
    return f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}"