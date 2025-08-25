from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from helpers.data import data_creators
from logger import logger
from data_fetchers.schools.de_anza_college_selenium.selenium_config import SeleniumConfig

driver = SeleniumConfig.create_driver()

def get_terms() -> list[dict]:
    driver.get("https://www.deanza.edu/schedule/")
    terms_holder = extract_terms_holder(driver)
    terms_options = terms_holder.find_elements(By.CSS_SELECTOR, "button[type='button']")
    terms_data = build_term_data_list(terms_options)
    input("Press Enter to continue... results: " + str(terms_data))
    return terms_data

def extract_terms_holder(driver: webdriver.Chrome) -> WebElement:
    terms_holder = _wait_for_element(driver, By.ID, "term-select")
    return terms_holder

def build_term_data_list(terms_options) -> list[dict]:
    term_data_list = []
    for term in terms_options:
        value = term.get_attribute("value")
        term_data = data_creators.create_term_data(term.text, value)
        term_data_list.append(term_data)

    return data_creators.process_term_data_list(term_data_list)

def _wait_for_element(driver: webdriver.Chrome, by: By, value: str) -> WebElement:
    try:
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        logger.error(f"Error waiting for {by} {value}: {e}")
        return None

if __name__ == "__main__":
    get_terms()