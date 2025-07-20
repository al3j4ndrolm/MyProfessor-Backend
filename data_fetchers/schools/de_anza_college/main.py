# Standard library imports
import sys
import os
import json
import logging
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local Imports
from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.de_anza_college.terms_fetcher import fetch_terms
from data_fetchers.schools.de_anza_college.courses_fetcher import get_course_names
from data_fetchers.schools.de_anza_college.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL
from data_fetchers.schools.de_anza_college.schedules_fetcher import get_schedules

logger = logging.getLogger(__name__)

def main() -> None:

    soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = fetch_terms(soup)
    # TODO: update terms_data_table to database `schools`

    term_codes = [ term["termCode"] for term in terms_data_table ]
    departments = get_departments(soup)
    courses_data_table, schedules_data_table = get_courses_and_schedules(departments, term_codes)
    # TODO: update courses_data_table to database `courses`
    # TODO: update schedules_data_table to database `schedules`

def get_departments(soup: BeautifulSoup) -> list:
    """
    Example of return value:
    [
        ("ACCT - Accounting", "ACCT"),
        ("BIO - Biology", "BIO"),
        ...
    ]   
    """

    try:
        department_elements_holder = soup.find("select", id="dept-select")
        department_elements = department_elements_holder.find_all("option")[1:]
    except Exception as e:
        logger.error(f"Error fetching department elements: {e}")
        return []

    department_name_code_list = []
    for element in department_elements:
        department_name_code_list.append((element.text, element.get("value")))

    return department_name_code_list
    
def get_courses_and_schedules(departments: list, term_codes: list) -> tuple[dict, dict]:
    
    courses_data_table = {}
    schedules_data_table = {term_code: {} for term_code in term_codes}

    for department_full_name, department_code in departments:

        courses_names = set()
        for term_code in term_codes:
            department_soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}") 
            schedules_data_table[term_code][department_code] = get_schedules(term_code, department_code, department_soup)
            courses_names.update(get_course_names(department_code, term_code, department_soup))
        courses_data_table[department_full_name] = courses_names

    return courses_data_table, schedules_data_table