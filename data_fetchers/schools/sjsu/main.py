# Standard library imports
import sys
import os
from supabase import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.schools.sjsu.terms import get_terms
from data_fetchers.schools.sjsu.courses import update_courses_data_table
from data_fetchers.schools.sjsu.schedules import get_classes_per_department
from data_fetchers.schools.sjsu.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.schools.common.pipeline import run_school_fetch
from logger import logger  # Import the configured logger instance

def main(supabase: Client, target_tables: set[str]) -> None:

    terms_soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(terms_soup)
    term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

    def get_courses_and_classes_lazy() -> tuple[dict, dict]:
        return get_courses_and_classes(term_codes)

    run_school_fetch(supabase, target_tables, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)

def get_courses_and_classes(term_codes: list) -> tuple[dict, dict]:
    courses_data_table = {}
    classes_data_table = {}
    departments = set()

    for term_code in term_codes:
        schedules_soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}{term_code}.php")

        # courses_data includes courses for all departments in one term, is a dict of str to sets
        update_courses_data_table(schedules_soup, courses_data_table)
        for department, _ in courses_data_table.items():
            departments.add(department)

        # schedules_data includes schedules for all departments in one term
        classes_data = get_classes_per_department(schedules_soup, departments)
        classes_data_table[term_code] = classes_data

    return courses_data_table, classes_data_table