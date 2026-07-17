from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import undetected_chromedriver as uc

from logger import logger
from data_fetchers.school_data.schools.de_anza_college_selenium.selenium_config import SeleniumConfig

def get_courses_per_department(department_code: str, driver: uc.Chrome) -> set:
    courses_elements_holder = _wait_for_element(driver, By.CSS_SELECTOR, ".table.table-schedule.table-hover.mix-container")
    courses_elements = courses_elements_holder.find_elements(By.TAG_NAME, "tr")
    courses_full_name_set = set()

    for course_element in courses_elements:
        course_full_name = get_course_full_name(course_element)
        if department_code in course_full_name:
            courses_full_name_set.add(course_full_name)
    return courses_full_name_set

def get_course_full_name(course_element: WebElement) -> str:
    course_data = course_element.find_elements(By.TAG_NAME, "td")
    if len(course_data) > 5:
        course_name = course_data[4].find_element(By.TAG_NAME, "a").text.strip()
        course_code = course_data[1].text.strip()
        return f"{course_code} - {course_name}"
    else:
        return ""

def _wait_for_element(driver: webdriver.Chrome, by: By, value: str) -> WebElement:
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))