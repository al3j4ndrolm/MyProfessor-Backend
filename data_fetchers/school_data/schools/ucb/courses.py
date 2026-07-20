# Standard library imports
import traceback

# Third Party Imports
from bs4 import BeautifulSoup, Tag

from logger import logger
from data_fetchers.school_data.schools.ucb.school_config import SCHOOL_NAME

def update_courses_data_table(department_soup: BeautifulSoup, department_code: str) -> set:
    """
    Returns the set of "COURSE_CODE - Course Title" strings found in a department's search results soup.
    """
    try:
        courses_elements = get_courses_elements(department_soup)

    except Exception as e:
        logger.error(f"Error getting courses for {SCHOOL_NAME} {department_code}: {traceback.format_exc()}")
        return set()

    courses = set()
    for course_element in courses_elements:
        course_code = get_course_code(course_element)
        course_name = get_course_name(course_element)

        if not course_code or not course_name:
            continue

        courses.add(f"{course_code} - {course_name}")

    return courses

def get_courses_elements(department_soup: BeautifulSoup) -> list[Tag]:
    return department_soup.find_all("article", class_="st")

def get_course_code(course_element: Tag) -> str:
    section_name = course_element.find("span", class_="st--section-name")
    return section_name.get_text().strip() if section_name else ""

def get_course_name(course_element: Tag) -> str:
    title = course_element.find("div", class_="st--title")
    if title is None:
        return ""

    heading = title.find("h2")
    return heading.get_text().strip() if heading else ""
