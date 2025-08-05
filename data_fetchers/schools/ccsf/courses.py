# Standard library imports
import traceback

# Third Party Imports
from bs4 import BeautifulSoup, Tag

from logger import logger
from school_config import SCHOOL_NAME

def get_courses_per_department(department_soup: BeautifulSoup, courses_data_table: dict, department_code: str) -> None:
    """
    Update the courses data table for a department.
    """
    try:
        courses_elements = get_courses_elements(department_soup)
        
    except Exception as e:
        logger.error(f"Error getting courses for {SCHOOL_NAME} {department_code}: {traceback.format_exc()}")
        return

    for course_element in courses_elements:
        course_code = get_course_code(course_element)
        course_name = get_course_name(course_element)
        course_full_name = f"{course_code} - {course_name}"
        
        courses_data_table[department_code].add(course_full_name)

def get_courses_elements(department_soup: BeautifulSoup) -> list[Tag]:
    # TODO: Implement based on your school's structure
    
    return []

def get_course_code(course_element: Tag) -> str:
    # TODO: Implement based on your school's structure
    
    return ""

def get_course_name(course_element: Tag) -> str:
    # TODO: Implement based on your school's structure
    
    return "" 