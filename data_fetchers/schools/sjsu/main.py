# Standard library imports
import sys
import os
from supabase import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys, data_creators
from data_fetchers.schools.sjsu.terms import get_terms
from data_fetchers.schools.sjsu.courses import update_courses_data_table
from data_fetchers.schools.sjsu.schedules import get_classes_per_department
from data_fetchers.ratings.rating_provider import get_ratings_and_merge
from data_fetchers.schools.sjsu.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from database import courses_db, classes_db, schools_db, professors_db
from logger import logger  # Import the configured logger instance

def main(supabase: Client, target_tables: set[str]) -> None:

    terms_soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(terms_soup)
    if "schools" in target_tables:
        logger.info("Start saving school data to database `schools`.")
        schools_db.save(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list)

    if "courses" in target_tables or "classes" in target_tables:
        term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]
        courses_data_table, classes_data_table = get_courses_and_classes(term_codes)

        if "courses" in target_tables:
            logger.info("Start saving data to database `courses`.")
            courses_db.save(supabase, courses_data_table, SCHOOL_NAME)

        if "classes" in target_tables:
            logger.info("Plugging in ratings data to classes data ...")
            for term_code, classes_all_departments in classes_data_table.items():
                for department_code, classes_one_department in classes_all_departments.items():
                    logger.info(f"Processing department {department_code} in term {term_code} ...")
                    get_ratings_and_merge(supabase, classes_one_department, SCHOOL_NAME, RMP_CODE, department_code)
                    logger.info(f"Saving classes data for {department_code} in term {term_code} to database `classes`.")
                    classes_db.save_one_entry(supabase, classes_one_department, SCHOOL_NAME, term_code, department_code)

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