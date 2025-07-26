# Standard library imports
import time
from supabase import Client

# Local Imports
from helpers.soup_getter import html_url_to_soup, get_soup_zenrows
from helpers.data import data_keys, data_creators
from data_fetchers.schools.de_anza_college.departments import get_departments
from data_fetchers.schools.de_anza_college.terms import get_terms
from data_fetchers.schools.de_anza_college.courses import get_courses_per_department
from data_fetchers.schools.de_anza_college.schedules import get_schedules_per_department
from data_fetchers.schools.de_anza_college.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from database import courses_db, schools_db, classes_db, professors_db
from logger import logger  # Import the configured logger instance

def main(supabase: Client, target_tables: set[str]) -> None:

    soup = get_soup_zenrows(TERMS_BASE_URL)
    terms_data_list = get_terms(soup)
    if "schools" in target_tables:
        logger.info("Start saving school data to database `schools`.")
        schools_db.save(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list)

    if "courses" in target_tables or "classes" in target_tables or "professors" in target_tables:
        departments = get_departments(soup)
        term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]
        courses_data_table, classes_data_table = get_courses_and_classes(departments, term_codes)

        if "courses" in target_tables:
            logger.info("Start saving data to database `courses`.")
            courses_db.save(supabase, courses_data_table, SCHOOL_NAME)

        if "classes" in target_tables:
            logger.info("Start saving data to database `classes`.")
            classes_db.save(supabase, classes_data_table, SCHOOL_NAME)

        if "professors" in target_tables:
            professors_by_department = data_creators.get_professors(classes_data_table)
            logger.info("Start saving professors data to database `professors`.")
            for department, professors_data_table in professors_by_department.items():
                professors_db.save(supabase, professors_data_table, SCHOOL_NAME, department)
    
def get_courses_and_classes(departments: list, term_codes: list) -> tuple[dict, dict]:
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for department_full_name, department_code in departments:

        courses = set()
        for term_code in term_codes:
            department_soup = get_soup_zenrows(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}")

            logger.debug(f"Getting schedules for {department_full_name} in {term_code} ...")
            department_schedules = get_schedules_per_department(department_soup)
            classes_data_table[term_code][department_code] = department_schedules

            logger.debug(f"Extracting courses for {department_full_name} in {term_code} ...")
            courses_per_term = get_courses_per_department(department_code, department_soup)
            courses.update(courses_per_term)

            time.sleep(3)

        logger.info(f"Overall found {len(courses)} courses for {department_full_name}.")
        courses_data_table[department_code] = courses
        return courses_data_table, classes_data_table # TODO: remove this after testing

    return courses_data_table, classes_data_table
