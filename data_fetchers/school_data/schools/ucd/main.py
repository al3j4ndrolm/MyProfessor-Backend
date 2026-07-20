# Standard library imports
import time
from bs4 import BeautifulSoup
from supabase import Client

# Selenium Imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

# Local Imports
from helpers.data import data_keys
from data_fetchers.school_data.schools.ucd.terms import get_terms
from data_fetchers.school_data.schools.ucd.courses import update_courses_data_table
from data_fetchers.school_data.schools.ucd.schedules import get_classes_per_department
from data_fetchers.school_data.schools.ucd.departments import get_department_data_table
from data_fetchers.school_data.schools.ucd.school_config import TERMS_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.school_data.schools.ucd.selenium_config import SeleniumConfig
from data_fetchers.school_data.common.pipeline import run_school_fetch
from logger import logger

# UC Davis's registrar search sits behind a Cloudflare JS challenge, so it's driven with a
# real browser (Selenium) instead of a plain requests.get() like most other schools.
_SEARCHING_TEXT = '<p class="workingText">Searching Courses Database....</p>'
_SEARCH_TIMEOUT_SECONDS = 20

def main(supabase: Client) -> None:
    driver = SeleniumConfig.create_driver(headless=False)

    try:
        driver.get(TERMS_BASE_URL)
        WebDriverWait(driver, _SEARCH_TIMEOUT_SECONDS).until(
            lambda d: d.find_elements(By.ID, "term") and d.find_elements(By.ID, "subject")
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        terms_data_list = get_terms(soup)
        term_codes = [term[data_keys.TERM_CODE_KEY] for term in terms_data_list]

        def get_courses_and_classes_lazy() -> tuple[dict, dict]:
            department_data_table = get_department_data_table(soup)
            return get_courses_and_classes(department_data_table, term_codes, driver)

        run_school_fetch(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)
    finally:
        driver.quit()

def get_courses_and_classes(department_data_table: dict, term_codes: list, driver: WebDriver) -> tuple[dict, dict]:
    """
    Get the courses and classes from the search results for every department/term combination.
    """
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for department_code in department_data_table.keys():
        courses = set()
        for term_code in term_codes:

            logger.debug(f"Getting classes for {department_code} in {term_code} ...")
            department_soup = _search_department(driver, department_code, term_code)

            classes_per_department = get_classes_per_department(department_soup, department_code)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            courses_per_term = update_courses_data_table(department_soup, department_code)
            courses.update(courses_per_term)

            # time.sleep(1)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table

def _search_department(driver: WebDriver, department_code: str, term_code: str) -> BeautifulSoup:
    """
    Selects the subject/term on the class search form, submits it, and waits for the
    AJAX results panel (#courseResultsDiv) to be populated.
    """
    try:
        Select(driver.find_element(By.ID, "subject")).select_by_value(department_code)
        Select(driver.find_element(By.ID, "term")).select_by_value(term_code)
        driver.find_element(By.CSS_SELECTOR, "input[name='search']").click()

        WebDriverWait(driver, _SEARCH_TIMEOUT_SECONDS).until(
            lambda d: d.find_element(By.ID, "courseResultsDiv").get_attribute("innerHTML").strip() not in ("", _SEARCHING_TEXT)
        )

        results_html = driver.find_element(By.ID, "courseResultsDiv").get_attribute("innerHTML")
        return BeautifulSoup(results_html, "html.parser")

    except Exception as e:
        logger.error(f"Error searching {department_code} for term {term_code}: {e}")
        return BeautifulSoup("", "html.parser")
