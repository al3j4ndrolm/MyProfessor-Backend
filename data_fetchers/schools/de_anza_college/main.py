# Standard library imports
import sys
import os
import json
import logging
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local Imports
from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.de_anza_college.departments import get_departments
from data_fetchers.schools.de_anza_college.terms import get_terms
from data_fetchers.schools.de_anza_college.courses import get_course_names
from data_fetchers.schools.de_anza_college.schedules import get_schedules
from data_fetchers.schools.de_anza_college.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL

logger = logging.getLogger(__name__)

def main() -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = get_terms(soup)
    # TODO: update terms_data_table to database `schools`

    departments = get_departments(soup)

    term_codes = [ term["termCode"] for term in terms_data_table ]
    courses_data_table, schedules_data_table = get_courses_and_schedules(departments, term_codes)
    # TODO: update courses_data_table to database `courses`
    # TODO: update schedules_data_table to database `schedules`
    
def get_courses_and_schedules(departments: list, term_codes: list) -> tuple[dict, dict]:
    
    courses_data_table = {}
    schedules_data_table = {term_code: {} for term_code in term_codes}

    for department_full_name, department_code in departments:

        courses = set()
        for term_code in term_codes:
            department_soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}")

            logger.info(f"Getting schedules for {department_full_name} in {term_code} ...")
            schedules = get_schedules(department_soup)
            schedules_data_table[term_code][department_code] = schedules

            logger.info(f"Getting courses for {department_full_name} in {term_code} ...")
            courses_per_term = get_course_names(department_code, term_code, department_soup)
            courses.update(courses_per_term)

        logger.info(f"Got {len(courses)} courses for {department_full_name}.")
        courses_data_table[department_full_name] = courses

    return courses_data_table, schedules_data_table