import sys
import json
import os
import logging
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_fetchers.schools.foothill.terms import get_terms
from data_fetchers.schools.foothill.departments import get_departments
from data_fetchers.schools.foothill.courses import get_courses
from data_fetchers.schools.foothill.schedules import get_schedules
from data_fetchers.schools.foothill.school_config import SCHEDULES_BASE_URL, TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup

logger = logging.getLogger(__name__)

def main() -> None:
    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = get_terms(soup)
    # TODO: update terms_data_table to database `schools`
    
    departments = get_departments(soup)
    departments = [("Accounting", "ACTG")] # TODO: remove this
    term_codes = [ term["termCode"] for term in terms_data_table ]
    term_codes = ["2025F"] # TODO: remove this
    courses_data_table, schedules_data_table = get_courses_and_schedules(departments, term_codes)
    # print(courses_data_table)
    print(json.dumps(schedules_data_table, indent=2))
    # TODO: update courses_data_table to database `courses`
    # TODO: update schedules_data_table to database `schedules`


def get_courses_and_schedules(departments: list, term_codes: list) -> tuple[dict, dict]:
    """
    Get the courses and schedules from the soup.
    """
    courses_data_table = {}
    schedules_data_table = {term_code: {} for term_code in term_codes}
    for department_full_name, department_code in departments:

        courses_names = set()
        for term_code in term_codes:
            department_url = f"{SCHEDULES_BASE_URL}?dept={department_code}%7C{department_full_name}&Quarter={term_code}"
            department_soup = html_url_to_soup(department_url)
            print(department_url)
            schedules_data_table[term_code][department_code] = get_schedules(department_soup)
            courses_names.update(get_courses(department_soup))
        courses_data_table[department_full_name] = courses_names

    return courses_data_table, schedules_data_table

if __name__ == "__main__":
    main()