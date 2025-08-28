import sys
import os
import time
from supabase import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from helpers.data import data_keys
from data_fetchers.rmp.ratings.rating_provider import get_ratings_and_merge
from data_fetchers.schools.foothill.terms import get_terms
from data_fetchers.schools.foothill.departments import get_department_data_table
from data_fetchers.schools.foothill.courses import update_courses_data_table
from data_fetchers.schools.foothill.schedules import get_classes_per_department
from data_fetchers.schools.foothill.school_config import SCHEDULES_BASE_URL, TERMS_BASE_URL, SCHOOL_NAME, RMP_CODE
from helpers.soup_getter import html_url_to_soup
from database import schools_db, courses_db, classes_db
from database.schools_db import SchoolStatus
from logger import logger

def main(supabase: Client, target_tables: set[str]) -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_list = get_terms(soup)
    if "schools" in target_tables:
        logger.info("Saving school data to database `schools`.")
        schools_db.save(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list)

    if "courses" in target_tables or "classes" in target_tables:
        department_data_table = get_department_data_table(soup)
        term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]
        courses_data_table, classes_data_table = get_courses_and_classes(department_data_table, term_codes)

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
    
    logger.info(f"Completed fetching. Setting {SCHOOL_NAME} status to `ready`.")
    schools_db.set_status(supabase, SCHOOL_NAME, SchoolStatus.READY.value)

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
