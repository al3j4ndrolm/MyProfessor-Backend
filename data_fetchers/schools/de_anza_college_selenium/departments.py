from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import undetected_chromedriver as uc

from logger import logger
from data_fetchers.schools.de_anza_college_selenium.selenium_config import SeleniumConfig

def get_department_data_table(driver: uc.Chrome) -> dict:

    logger.info("inside get_department_data_table")
    department_elements_holder = _wait_for_element(driver, By.NAME, "dept-select")
    department_elements = department_elements_holder.find_elements(By.TAG_NAME, "option")
    department_data_table = {}

    logger.info(f"Found {len(department_elements)} departments.")

    for element in department_elements:
        department_name = " - ".join(element.text.split(" - ")[1:]).strip()
        department_code = element.get_attribute("value").strip()
        department_data_table[department_code] = department_name

    logger.info(f"department_data_table: {department_data_table}")
    return department_data_table

def _wait_for_element(driver: webdriver.Chrome, by: By, value: str) -> WebElement:
    try:
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        logger.error(f"departments.py: Error waiting for {by} {value}: {e}")
        return None

# TODO: Remove this
if __name__ == "__main__":
    driver = SeleniumConfig.create_driver(headless=False)
    driver.get("https://www.deanza.edu/schedule/")
    print(get_department_data_table(driver))