# Standard library imports
from bs4 import BeautifulSoup

from logger import logger

def update_courses_data_table(department_soup: BeautifulSoup, courses_data_table: dict) -> None:
    try:
        logger.debug(f"Extracting courses for San Jose State University ...")

        courses_fieldset = department_soup.find("table", id="classSchedule")
        if courses_fieldset is None:
            raise ValueError("Courses holder not found in soup for San Jose State University")
        courses_options = courses_fieldset.find_all("tr")[1:]

        for course_row in courses_options:
            course_data = course_row.find_all("td")
            course_name = course_data[0].text.strip().split(' (')[0]
            course_title = course_data[3].text.strip()
            department_code = course_name.split(' ')[0]

            if department_code not in courses_data_table:
                courses_data_table[department_code] = set()
            courses_data_table[department_code].add(course_name + " - " + course_title)
    except Exception as e:
        logger.error(f"Error getting courses for San Jose State University: {e}")
