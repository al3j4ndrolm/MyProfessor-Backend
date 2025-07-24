# Standard library imports
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def update_courses_data_table(soup: BeautifulSoup, courses_data_table: dict) -> None:
    try:
        logger.info(f"Extracting courses for San Jose State University ...")

        courses_fieldset = soup.find("table", id="classSchedule")
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

        logger.info(f"Extracted courses for {len(courses_data_table)} departments for San Jose State University")
    except Exception as e:
        logger.error(f"Error getting courses for San Jose State University: {e}")
