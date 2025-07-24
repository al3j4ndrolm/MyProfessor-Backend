# Standard library imports
import sys
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local Imports
from helpers.soup_getter import html_url_to_soup
from data_fetchers.api.terms.configs import TERM_CODE_KEY
from data_fetchers.schools.sjsu.terms import get_terms
from data_fetchers.schools.sjsu.courses import update_courses_data_table
from data_fetchers.schools.sjsu.schedules import get_schedules_all_departments
from data_fetchers.schools.sjsu.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from database.courses import save_courses_data
from database.classes import save_classes_data
from database.schools import save_schools_data

logger = logging.getLogger(__name__)

def main() -> None:

    terms_soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = get_terms(terms_soup)

    term_codes = [ term[TERM_CODE_KEY] for term in terms_data_table ]
    courses_data_table, classes_data_table = get_courses_and_classes(term_codes)

    # Save data to database
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)

    save_schools_data(supabase, SCHOOL_NAME, RMP_CODE, terms_data_table)
    save_courses_data(supabase, courses_data_table, SCHOOL_NAME)
    save_classes_data(supabase, classes_data_table, SCHOOL_NAME)


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