import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import undetected_chromedriver as uc

# Local imports
from helpers.data import data_creators, data_keys
from logger import logger
from data_fetchers.school_data.de_anza_college_selenium.selenium_config import SeleniumConfig

def get_classes_per_department(department_code: str, driver: uc.Chrome) -> dict:

    schedules_holder = _wait_for_element(driver, By.CSS_SELECTOR, "table[class*='table-schedule']")
    if schedules_holder is None:
        logger.warning(f"schedules.py: No schedules found for {department_code}.")
        return {}
    
    try:
        schedules_options = schedules_holder.find_elements(By.TAG_NAME, "tr")
        schedule_data_table = build_classes_data_table(schedules_options[1:], department_code)
        logger.info(f"Extracted classes for {len(schedule_data_table)} courses.")
        return schedule_data_table
    except Exception as e:
        logger.error(f"Error getting classes per department: {traceback.format_exc()}")
        return {}

def build_classes_data_table(schedule_rows: list[WebElement], department_code: str) -> dict:

    classes_data_table = {}
    last_course_name = None
    last_professor_identifier = None

    for schedule_row in schedule_rows:
        schedule_tags = schedule_row.find_elements(By.TAG_NAME, "td")
        if len(schedule_tags) > 5:
            course_code = schedule_tags[1].text
            professor_name = schedule_tags[7].text

            professor_links = schedule_tags[7].find_elements(By.TAG_NAME, "a")
            professor_id = None
            if professor_links:
                try:
                    professor_id = professor_links[0].get_attribute("href").split("=")[1]
                except Exception:
                    logger.error(f"schedules.py: Error parsing professor ID: {traceback.format_exc()}")

            professor_email = f"{professor_id}@deanza.edu" if professor_id else None
            professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)

            last_course_code = course_code
            last_professor_identifier = professor_identifier

            if department_code not in course_code:
                continue

            if course_code not in classes_data_table:
                classes_data_table[course_code] = {}

            if professor_identifier not in classes_data_table[course_code]:
                professor_data = data_creators.create_professor_data(email = professor_email)
                classes_data_table[course_code][professor_identifier] = professor_data

            class_data = _get_class_data(schedule_tags)
            if class_data == {}:
                continue

            classes_data_table[course_code][professor_identifier][data_keys.PROFESSOR_CLASSES_KEY].append(class_data)
        
        else:
            meeting_data = _get_meeting_data(schedule_tags)
            if meeting_data == {}:
                continue
            
            professor_data = classes_data_table[last_course_code][last_professor_identifier]
            class_data = professor_data[data_keys.PROFESSOR_CLASSES_KEY][-1]
            class_data[data_keys.MEETINGS_KEY].append(meeting_data)

    return classes_data_table

def _get_class_data(schedule_tags: list[WebElement]) -> dict:

    try:
        class_crn = schedule_tags[0].text
        availability = schedule_tags[3].text
        days = schedule_tags[5].text
        time = schedule_tags[6].text
        location = schedule_tags[8].text
    except Exception as e:
        logger.error(f"Error getting class data by index: {e}")
        return {}
    
    class_data = data_creators.create_class_data(class_crn, availability)
    meeting_data = data_creators.create_meeting_data(tag = "", days = days, time = time, location = location)
    class_data[data_keys.MEETINGS_KEY].append(meeting_data)
    return class_data

def _get_meeting_data(schedule_tags: list[WebElement]) -> dict:
    tag = schedule_tags[0].text.strip()

    if tag == "":
        logger.warning(f"schedules.py: Tag is empty. Skipping meeting.")
        return {}
    
    meeting_data = data_creators.create_meeting_data(
        tag = "" if tag == "CLAS" else tag,
        days = schedule_tags[1].text,
        time = schedule_tags[2].text,
        location = schedule_tags[4].text
    )
    return meeting_data

def _wait_for_element(driver: uc.Chrome, by: By, value: str) -> WebElement | None:
    try:
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        logger.error(f"schedules.py: Error waiting for {by} {value}")
        return None
