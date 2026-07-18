# Standard library imports
import time
from supabase import Client

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.school_data.schools.de_anza_college.departments import get_department_data_table
from data_fetchers.school_data.schools.de_anza_college.terms import get_terms
from data_fetchers.school_data.schools.de_anza_college.courses import get_courses_per_department
from data_fetchers.school_data.schools.de_anza_college.schedules import get_classes_per_department
from data_fetchers.school_data.schools.de_anza_college.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.school_data.common.pipeline import run_school_fetch
from logger import logger  # Import the configured logger instance

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
            department_soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}")

            logger.debug(f"Getting schedules for {department_code} in {term_code} ...")
            classes_per_department = get_classes_per_department(department_soup, department_code)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            courses_per_term = get_courses_per_department(department_code, department_soup)
            courses.update(courses_per_term)

            time.sleep(3)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table

