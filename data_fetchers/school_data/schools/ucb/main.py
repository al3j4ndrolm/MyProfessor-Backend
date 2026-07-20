# Standard library imports
import time
from bs4 import BeautifulSoup
from supabase import Client

# Local Imports
from helpers.data import data_keys
from data_fetchers.school_data.schools.ucb.terms import get_terms
from data_fetchers.school_data.schools.ucb.courses import update_courses_data_table
from data_fetchers.school_data.schools.ucb.schedules import get_classes_per_department
from data_fetchers.school_data.schools.ucb.departments import get_department_data_table
from data_fetchers.school_data.schools.ucb.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE
from data_fetchers.school_data.common.pipeline import run_school_fetch
from data_fetchers.school_data.schools.de_anza_college_selenium.selenium_config import SeleniumConfig
from logger import logger

# Safety cap on paginated search results per department/term to avoid infinite loops.
_MAX_PAGES = 50

def main(supabase: Client) -> None:

    driver = SeleniumConfig.create_driver(headless=True)
    try:
        soup = _load_soup(driver, TERMS_BASE_URL)
        terms_data_list = get_terms(soup)
        term_codes = [ term[data_keys.TERM_CODE_KEY] for term in terms_data_list ]

        def get_courses_and_classes_lazy() -> tuple[dict, dict]:
            department_data_table = get_department_data_table(soup)
            return get_courses_and_classes(driver, department_data_table, term_codes)

        run_school_fetch(supabase, SCHOOL_NAME, RMP_CODE, terms_data_list, get_courses_and_classes_lazy)
    finally:
        driver.quit()

def get_courses_and_classes(driver, department_data_table: dict, term_codes: list) -> tuple[dict, dict]:
    """
    Get the courses and classes from the soup.
    """
    courses_data_table = {}
    classes_data_table = {term_code: {} for term_code in term_codes}

    for department_code in department_data_table.keys():
        courses = set()
        for term_code in term_codes:

            logger.debug(f"Getting classes for {department_code} in {term_code} ...")
            department_soup = _get_department_soup(driver, department_code, term_code)

            classes_per_department = get_classes_per_department(department_soup, department_code)
            classes_data_table[term_code][department_code] = classes_per_department

            logger.debug(f"Extracting courses for {department_code} in {term_code} ...")
            courses_per_term = update_courses_data_table(department_soup, department_code)
            courses.update(courses_per_term)

            time.sleep(1)

        logger.info(f"Overall found {len(courses)} courses for {department_code}.")
        courses_data_table[department_code] = courses

    return courses_data_table, classes_data_table

def _get_department_soup(driver, department_code: str, term_code: str) -> BeautifulSoup:
    """
    UCB's search results are paginated (~18 results per page), so results for a
    department/term are fetched page by page and merged into a single soup.
    """
    combined_soup = BeautifulSoup("<div></div>", "html.parser")
    container = combined_soup.div

    for page in range(_MAX_PAGES):
        page_url = f"{SCHEDULES_BASE_URL}?f[0]=subject_area:{department_code}&f[1]=term:{term_code}&page={page}"
        page_soup = _load_soup(driver, page_url)
        if page_soup is None:
            break

        articles = page_soup.find_all("article", class_="st")
        if not articles:
            break

        for article in articles:
            container.append(article)

        has_next_page = page_soup.find("li", class_="pager__item--next") is not None
        if not has_next_page:
            break

    return combined_soup

def _load_soup(driver, url: str) -> BeautifulSoup | None:
    try:
        driver.get(url)
        return BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None
