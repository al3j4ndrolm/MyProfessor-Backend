# Standard library imports
import time
import requests
from bs4 import BeautifulSoup
from supabase import Client

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.school_data.schools.ucsc.terms import get_terms
from data_fetchers.school_data.schools.ucsc.courses import update_courses_data_table
from data_fetchers.school_data.schools.ucsc.schedules import get_classes_per_department
from data_fetchers.school_data.schools.ucsc.departments import get_department_data_table
from data_fetchers.school_data.schools.ucsc.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE, RESULTS_PER_PAGE
from data_fetchers.school_data.common.pipeline import run_school_fetch
from logger import logger

_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

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

    for department_code in department_data_table.keys():
        courses = set()
        for term_code in term_codes:

            logger.debug(f"Getting classes for {department_code} in {term_code} ...")
            department_soup = _get_department_soup(department_code, term_code)

            classes_per_department = get_classes_per_department(department_soup, department_code)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            courses_per_term = update_courses_data_table(department_soup, department_code)
            courses.update(courses_per_term)

            time.sleep(1)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table

def _get_department_soup(department_code: str, term_code: str) -> BeautifulSoup:
    payload = {
        "action": "results",
        "binds[:term]": term_code,
        "binds[:session_code]": "",
        "binds[:reg_status]": "all",
        "binds[:subject]": department_code,
        "binds[:catalog_nbr_op]": "=",
        "binds[:catalog_nbr]": "",
        "binds[:title]": "",
        "binds[:instr_name_op]": "contains",
        "binds[:instructor]": "",
        "binds[:ge]": "",
        "binds[:crse_units_op]": "=",
        "binds[:crse_units_exact]": "",
        "binds[:days]": "",
        "binds[:times]": "",
        "binds[:acad_career]": "",
        "binds[:asynch]": "A",
        "binds[:hybrid]": "H",
        "binds[:synch]": "S",
        "binds[:person]": "P",
        "rec_start": "0",
        "rec_dur": str(RESULTS_PER_PAGE),
    }

    try:
        response = requests.post(SCHEDULES_BASE_URL, data=payload, headers={"User-Agent": _USER_AGENT})
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.error(f"Error fetching {department_code} for term {term_code}: {e}")
        return BeautifulSoup("", "html.parser")
