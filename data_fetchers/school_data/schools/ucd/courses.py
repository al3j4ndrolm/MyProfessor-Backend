# Standard library imports
import traceback

# Third Party Imports
from bs4 import BeautifulSoup, Tag

from logger import logger
from data_fetchers.school_data.schools.ucd.school_config import SCHOOL_NAME

def update_courses_data_table(department_soup: BeautifulSoup, department_code: str) -> set:
    """
    Returns the set of "COURSE_CODE - Course Title" strings found in a department's search results soup.
    """
    try:
        courses_elements = get_courses_elements(department_soup)

    except Exception:
        logger.error(f"Error getting courses for {SCHOOL_NAME} {department_code}: {traceback.format_exc()}")
        return set()

    courses = set()
    for course_element in courses_elements:
        course_code, _, course_name = parse_course_row(course_element)

        if not course_code or not course_name:
            continue

        courses.add(f"{course_code} - {course_name}")

    return courses

def get_courses_elements(department_soup: BeautifulSoup) -> list[Tag]:
    results_table = department_soup.find("table", id="mc_win")
    if results_table is None:
        return []

    return [row for row in results_table.find_all("tr") if row.find("th", attrs={"scope": "row"})]

def get_course_code(course_element: Tag) -> str:
    course_code, _, _ = parse_course_row(course_element)
    return course_code

def get_course_name(course_element: Tag) -> str:
    _, _, course_name = parse_course_row(course_element)
    return course_name

def parse_course_row(course_element: Tag) -> tuple[str, str, str]:
    """
    Parses a class search result row.

    Example cells: ["ECS 032A", "A01  25/0", "Intro to Programming  SE", "The Staff  4.0", "view 28914"]
    Returns: ("ECS 032A", "A01", "Intro to Programming")
    """
    cells = course_element.find_all("td")
    if len(cells) < 3:
        return "", "", ""

    course_code = cells[0].get_text(strip=True)
    section = cells[1].get_text(separator="|", strip=True).split("|")[0].strip()
    course_name = cells[2].get_text(separator="|", strip=True).split("|")[0].strip()

    return course_code, section, course_name
