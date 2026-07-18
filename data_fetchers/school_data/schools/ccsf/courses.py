# Standard library imports
import re
import traceback

# Third Party Imports
from bs4 import BeautifulSoup, Tag

from logger import logger
from data_fetchers.school_data.schools.ccsf.school_config import SCHOOL_NAME

def update_courses_data_table(department_soup: BeautifulSoup, courses_data_table: dict, department_code: str) -> None:
    """
    Update the courses data table for a department.
    """
    try:
        courses_elements = get_courses_elements(department_soup)
        
    except Exception as e:
        logger.error(f"Error getting courses for {SCHOOL_NAME} {department_code}: {traceback.format_exc()}")
        return

    for course_element in courses_elements:
        course_data = course_element.find_all('td')
        course_code = f"{course_data[2].text.strip()} {course_data[3].text.strip()}"
        course_name = course_data[5].text.strip()
        course_full_name = f"{course_code} - {course_name}"
        
        if department_code in course_code:
            courses_data_table[department_code].add(course_full_name)

def get_courses_elements(department_soup: BeautifulSoup) -> list[Tag]:

    courses_table = department_soup.find('table', attrs={'class': re.compile(r'^cols-18')})

    if courses_table is None:
        logger.warning("No courses table found in the HTML structure of CCSF")
        return []
    
    return courses_table.find_all('tr', attrs={'class': re.compile(r'^course-data')})