# Standard library imports
import time
import math
from supabase import Client
from bs4 import BeautifulSoup

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.ratings.rating_provider import get_ratings_and_merge
from data_fetchers.schools.ccsf.terms import get_terms
from data_fetchers.schools.ccsf.courses import update_courses_data_table
from data_fetchers.schools.ccsf.schedules import update_classes_data_table
from data_fetchers.schools.ccsf.departments import get_department_data_table
from data_fetchers.schools.ccsf.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from database import courses_db, schools_db, classes_db
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
    
    logger.info(f"Completed fetching. Setting {SCHOOL_NAME} status to `supported`.")
    schools_db.set_status(supabase, SCHOOL_NAME, SchoolStatus.READY.value)

def get_courses_and_classes(department_data_table: dict, term_codes: list) -> tuple[dict, dict]:
    """
    Get the courses and classes from the soup.
    """
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for term_code in term_codes:

        initial_page_url = _get_page_url(term_code, 0)
        initial_page_soup = html_url_to_soup(initial_page_url)
        number_of_pages = get_number_of_pages(initial_page_soup)

        for page_number in range(0, number_of_pages):
            page_url = _get_page_url(term_code, page_number)
            page_soup = html_url_to_soup(page_url)

            update_classes_data_table(page_soup, classes_data_table)
            update_courses_data_table(page_soup, courses_data_table)

        time.sleep(1)

    return courses_data_table, classes_data_table

def _get_page_url(term_code: str, page_number: int) -> str:
    # TODO: Modify this based on your school's url structure
    return f"{SCHEDULES_BASE_URL}?field_term_target_id={term_code}&field_course_credit_value=All&field_campus_taxonomy_target_id=All&field_crn_value=&field_parent_program_target_id=All&field_diversity_target_id=All&field_ge_area_target_id=All&field_instructor_target_id=&field_ztc_code_value=All&field_start_hour_value=All&field_start_minute_value=All&field_start_period_value=All&field_end_hour_value=All&field_end_minute_value=All&field_end_period_value=All&items_per_page=50&page={page_number}"

def get_number_of_pages(soup: BeautifulSoup) -> int:
    """
    Get the number of pages from the soup.
    """
    pagination_element = soup.find("div", id="paging-summary")
    if pagination_element is None:
        return 1
    courses_num = int(pagination_element.find_all("strong")[1].text)
    items_per_page = 50
    return math.ceil(courses_num / items_per_page)