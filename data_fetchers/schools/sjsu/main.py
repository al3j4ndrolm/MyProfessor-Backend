# Standard library imports
import sys
import os
import logging
from supabase import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.schools.sjsu.terms import get_terms
from data_fetchers.schools.sjsu.courses import update_courses_data_table
from data_fetchers.schools.sjsu.schedules import get_schedules_all_departments
from data_fetchers.schools.sjsu.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from database import courses_db, classes_db, schools_db

logger = logging.getLogger(__name__)

def main(supabase: Client) -> None:

    terms_soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(terms_soup)
    # Save data to database
    schools_db.save(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list)

    term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]
    courses_data_table, classes_data_table = get_courses_and_classes(term_codes)

    # Save data to database
    logger.info("Start saving data for San Jose State University to database.")
    courses_db.save(supabase, courses_data_table, SCHOOL_NAME)
    classes_db.save(supabase, classes_data_table, SCHOOL_NAME)

def get_courses_and_classes(term_codes: list) -> tuple[dict, dict]:
    courses_data_table = {}
    classes_data_table = {}
    departments = set()

    for term_code in term_codes:
        schedules_soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}{term_code}")

        # courses_data includes courses for all departments in one term, is a dict of str to sets
        update_courses_data_table(schedules_soup, courses_data_table)
        for department, _ in courses_data_table.items():
            departments.add(department)

        # schedules_data includes schedules for all departments in one term
        classes_data = get_schedules_all_departments(schedules_soup, departments)
        classes_data_table[term_code] = classes_data

    return courses_data_table, classes_data_table