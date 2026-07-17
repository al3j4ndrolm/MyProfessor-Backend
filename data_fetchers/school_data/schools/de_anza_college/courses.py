# Standard library imports
import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Third Party Imports
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

def get_courses_per_department(department_code: str, soup: BeautifulSoup) -> set:
    """
    Example of return value:
    {
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        ...
    }
    """
    courses_elements_holder = soup.find("table", class_="table table-schedule table-hover mix-container")
    if courses_elements_holder is None:
        return set()
    
    try:
        courses_elements = courses_elements_holder.find_all("tr")[1:]
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return set()

    courses_full_name_set = set()
    for course_element in courses_elements:
        course_full_name = get_course_full_name(course_element)
        if department_code in course_full_name:
            courses_full_name_set.add(course_full_name)
        
    return courses_full_name_set

def get_course_full_name(course_element: Tag) -> str:

    course_data = course_element.find_all("td")

    if len(course_data) > 5: # This is to avoid the case where the course data is a LAB or CLAS
        course_name = course_data[4].find("a").text.strip()
        course_code = course_data[1].text.strip()
        return f"{course_code} - {course_name}"
    else:
        return ""



