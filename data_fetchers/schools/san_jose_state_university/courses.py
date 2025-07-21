import logging
from bs4 import BeautifulSoup, Tag

from data_fetchers.api.courses.response import create_courses_data

logger = logging.getLogger(__name__)

def get_courses(soup: BeautifulSoup, courses_data_table: dict):

    try:
        logger.info(f"Getting courses for San Jose State University")
        courses_fieldset = get_courses_fieldset(soup)
        courses_options = get_courses_options(courses_fieldset)
        courses_data_table = build_courses_data_table(courses_options, courses_data_table)
        return courses_data_table

    except Exception as e:
        logger.error(f"Error getting courses for San Jose State University: {e}")
        return {}

def get_courses_fieldset(soup: BeautifulSoup) -> Tag:

    courses_holder = soup.find("table", id="classSchedule")

    if courses_holder is None:
        raise ValueError("Courses holder not found in soup for San Jose State University")

    return courses_holder

def get_courses_options(courses_fieldset: Tag) -> list[Tag]:

    try:
        courses_options = courses_fieldset.find_all("tr")[1:]
    except Exception as e:
        raise ValueError("Courses options not found in fieldset for San Jose State University")

    return courses_options

def build_courses_data_table(courses_rows: list[Tag], courses_data_table: dict) -> dict:

    for course_row in courses_rows:

        course_data = course_row.find_all("td")

        course_name = course_data[0].text.strip().split(' (')[0]
        course_title = course_data[1].text.strip()
        course_code = course_name.split(' ')[0]

        if course_code not in courses_data_table:
            courses_data_table[course_code] = [course_name]
        else:
            courses_data_table[course_code].append(course_name)

    return courses_data_table
