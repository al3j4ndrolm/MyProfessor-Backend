import sys
import os
import re
import time
from supabase import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from helpers.data import data_keys
from data_fetchers.school_data.foothill.terms import get_terms
from data_fetchers.school_data.foothill.departments import get_department_data_table
from data_fetchers.school_data.foothill.courses import update_courses_data_table
from data_fetchers.school_data.foothill.schedules import get_classes_per_department
from data_fetchers.school_data.foothill.professors import get_professor_data_table, update_professor_data_table
from data_fetchers.school_data.foothill.school_config import FACULTY_ALL_URL, SCHEDULES_BASE_URL, TERMS_BASE_URL, FACULTY_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.school_data.common.pipeline import run_school_fetch
from helpers.soup_getter import html_url_to_soup
from logger import logger

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

    all_faculty_soup = html_url_to_soup(FACULTY_ALL_URL)
    professor_data_table = get_professor_data_table(all_faculty_soup)

    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}
    for department_code, department_full_name in department_data_table.items():

        faculty_url = FACULTY_BASE_URL.replace("[dpmt]", _get_department_slug(department_full_name))
        faculty_soup = html_url_to_soup(faculty_url)
        if not faculty_soup:
            faculty_url = FACULTY_BASE_URL.replace("[dpmt]", department_code)
            faculty_soup = html_url_to_soup(faculty_url)
        if not faculty_soup:
            faculty_url = FACULTY_BASE_URL.replace("[dpmt]", department_code.replace("-", ""))
            faculty_soup = html_url_to_soup(faculty_url)
        update_professor_data_table(faculty_soup, department_code, professor_data_table)

        courses = set()
        for term_code in term_codes:
            department_url = f"{SCHEDULES_BASE_URL}?dept={department_code}%7C{department_full_name}&Quarter={term_code}"
            department_soup = html_url_to_soup(department_url)

            logger.debug(f"Getting classes for {department_code} in {term_code} ...")
            classes_per_department = get_classes_per_department(department_soup, professor_data_table, department_code)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            update_courses_data_table(department_soup, courses)

            time.sleep(3)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table

def _get_department_slug(department_full_name: str) -> str:
    """
    Best-effort mapping from a department's dropdown display name (e.g. "Allied Health
    Sciences") to its directory page URL slug (e.g. "allied-health-sciences"). Foothill's
    slugs aren't derived programmatically from the display name for every department (e.g.
    parenthetical/slash suffixes are dropped), so this won't resolve correctly in all cases.
    """
    slug = department_full_name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug
