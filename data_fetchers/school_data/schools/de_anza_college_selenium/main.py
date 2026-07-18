
# Standard library imports
import time
from supabase import Client

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys
from data_fetchers.school_data.schools.de_anza_college_selenium.departments import get_department_data_table
from data_fetchers.school_data.schools.de_anza_college_selenium.terms import get_terms
from data_fetchers.school_data.schools.de_anza_college_selenium.courses import get_courses_per_department
from data_fetchers.school_data.schools.de_anza_college_selenium.schedules import get_classes_per_department
from data_fetchers.school_data.schools.de_anza_college_selenium.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.school_data.common.pipeline import run_school_fetch
from logger import logger

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from data_fetchers.school_data.schools.de_anza_college_selenium.selenium_config import SeleniumConfig

def main(supabase: Client, target_tables: set[str]) -> None:

    driver = SeleniumConfig.create_driver(headless=False)
    driver.get(TERMS_BASE_URL)
    time.sleep(3)

    terms_data_list = get_terms(driver)
    logger.info(f"Found {len(terms_data_list)} terms.")
    term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

    def get_courses_and_classes_lazy() -> tuple[dict, dict]:
        logger.info("Getting departments ...")
        departments = sorted(list(get_department_data_table(driver).keys()))[1:]
        logger.info("now getting courses and classes ...")
        return get_courses_and_classes(departments, term_codes, driver)

    run_school_fetch(supabase, target_tables, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)

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