
# Standard library imports
import time
from supabase import Client

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.rmp.ratings.rating_provider import get_ratings_and_merge
from data_fetchers.schools.de_anza_college_selenium.departments import get_department_data_table
from data_fetchers.schools.de_anza_college_selenium.terms import get_terms
from data_fetchers.schools.de_anza_college_selenium.courses import get_courses_per_department
from data_fetchers.schools.de_anza_college_selenium.schedules import get_classes_per_department
from data_fetchers.schools.de_anza_college_selenium.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from database import courses_db, schools_db, classes_db
from database.schools_db import SchoolStatus
from logger import logger

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from data_fetchers.schools.de_anza_college_selenium.selenium_config import SeleniumConfig

def main(supabase: Client, target_tables: set[str]) -> None:

    driver = SeleniumConfig.create_driver(headless=True)
    driver.get(TERMS_BASE_URL)
    time.sleep(3)

    terms_data_list = get_terms(driver)
    logger.info(f"Found {len(terms_data_list)} terms.")

    if "schools" in target_tables:
        logger.info("Saving school data to database `schools`.")
        schools_db.save(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list)

    if "courses" in target_tables or "classes" in target_tables:
        logger.info("Getting departments ...")
        departments = sorted(list(get_department_data_table(driver).keys()))[1:]
        term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

        logger.info("now getting courses and classes ...")
        courses_data_table, classes_data_table = get_courses_and_classes(departments, term_codes, driver)

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
    schools_db.set_status(supabase, SCHOOL_NAME, SchoolStatus.SUPPORTED.value)

def get_courses_and_classes(departments: list, term_codes: list, driver: webdriver.Chrome) -> tuple[dict, dict]:
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for department_code in departments[1:]:
        courses = set()

        for term_code in term_codes:
            time.sleep(5)
            logger.info(f"getting new tab for schedules for {department_code} in {term_code} ...")
            driver.get(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}")

            logger.info(f"Getting schedules for {department_code} in {term_code} ...")
            classes_per_department = get_classes_per_department(department_code, driver)

            if classes_per_department == {}:
                logger.info(f"No classes found for {department_code} in {term_code}.")
                continue
            
            classes_data_table[term_code][department_code] = classes_per_department

            logger.info(f"Extracting courses for {department_code} in {term_code} ...")
            courses_per_term = get_courses_per_department(department_code, driver)
            courses.update(courses_per_term)

            time.sleep(5)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table