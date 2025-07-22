# Standard library imports
import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Third Party Imports
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

def get_course_names(department_code: str, soup: BeautifulSoup) -> set:
    """
    Example of return value:
    [
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        ...
    ]
    """

    try:
        courses_elements = get_courses_elements_holder(soup)
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return set()

    courses_full_name_set = set()
    for course_element in courses_elements:
        course_code, course_name = get_course_name_and_code(course_element)
        if department_code in course_code and course_code and course_name:
            courses_full_name_set.add(f"{course_code} - {course_name}")
        
    return courses_full_name_set

def get_courses_elements_holder(soup: BeautifulSoup) -> list[Tag]:

    courses_elements_holder = soup.find("table", class_="table table-schedule table-hover mix-container")
    courses_elements = courses_elements_holder.find_all("tr")[1:]
    return courses_elements

def get_course_name_and_code(course_element: Tag) -> tuple[str, str]:

    course_data = course_element.find_all("td")

    if len(course_data) > 5: # This is to avoid the case where the course data is a LAB or CLAS
        course_name = course_data[4].find("a").text.strip()
        course_code = course_data[1].text.strip()
        return course_code, course_name
    else:
        return "", ""



