import sys
import os
import time
from supabase import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from helpers.data import data_keys
from data_fetchers.schools.foothill.terms import get_terms
from data_fetchers.schools.foothill.departments import get_department_data_table
from data_fetchers.schools.foothill.courses import update_courses_data_table
from data_fetchers.schools.foothill.schedules import get_classes_per_department
from data_fetchers.schools.foothill.school_config import SCHEDULES_BASE_URL, TERMS_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.schools.common.pipeline import run_school_fetch
from helpers.soup_getter import html_url_to_soup
from logger import logger

def main(supabase: Client, target_tables: set[str]) -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(soup)
    term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

    def get_courses_and_classes_lazy() -> tuple[dict, dict]:
        department_data_table = get_department_data_table(soup)
        return get_courses_and_classes(department_data_table, term_codes)

    run_school_fetch(supabase, target_tables, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)

def get_courses_and_classes(department_data_table: dict, term_codes: list) -> tuple[dict, dict]:
    """
    Get the courses and classes from the soup.
    """
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}
    for department_code, department_full_name in department_data_table.items():

        courses = set()
        for term_code in term_codes:
            department_url = f"{SCHEDULES_BASE_URL}?dept={department_code}%7C{department_full_name}&Quarter={term_code}"
            department_soup = html_url_to_soup(department_url)

            logger.debug(f"Getting classes for {department_code} in {term_code} ...")
            classes_per_department = get_classes_per_department(department_soup)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            update_courses_data_table(department_soup, courses)

            time.sleep(3)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table
