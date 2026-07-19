# Standard library imports
import re
import traceback

# Third Party Imports
from bs4 import BeautifulSoup, Tag

from logger import logger
from data_fetchers.school_data.schools.ucsc.school_config import SCHOOL_NAME

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
    return department_soup.find_all("div", id=re.compile(r"^rowpanel_\d+$"))

def get_course_code(course_element: Tag) -> str:
    course_code, _, _ = parse_course_header(course_element)
    return course_code

def get_course_name(course_element: Tag) -> str:
    _, _, course_name = parse_course_header(course_element)
    return course_name

def parse_course_header(course_element: Tag) -> tuple[str, str, str]:
    """
    Parses a class result panel's heading.

    Example heading text: "CSE 3 - 01   Comp Tech in Society"
    Returns: ("CSE 3", "01", "Comp Tech in Society")
    """
    heading = course_element.find("h2")
    title_link = heading.find("a") if heading else None
    if title_link is None:
        return "", "", ""

    text = title_link.get_text().replace("\xa0", " ")
    course_code, _, rest = text.partition(" - ")
    section, _, course_name = rest.strip().partition(" ")

    return course_code.strip(), section.strip(), course_name.strip()
