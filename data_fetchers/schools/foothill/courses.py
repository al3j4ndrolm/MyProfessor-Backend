# Standard library imports
from bs4 import BeautifulSoup

from logger import logger

def update_courses_data_table(department_soup: BeautifulSoup, courses_data_table: dict) -> None:
    """
    Get the courses from the soup for a department and term.
    """
    # Find all course blocks
    try:
        for course_block in department_soup.find_all("div", class_="fh_sched-grid-2-8-2"):
            course_id_tag = course_block.find("h3", class_="fh_course-id")
            course_title_tag = course_block.find("h3", class_="fh_course-head")
            if course_id_tag and course_title_tag:
                course_id = course_id_tag.text.strip()
                course_title = course_title_tag.text.strip()
                courses_data_table.add(f"{course_id} - {course_title}")
    except Exception as e:
        logger.error(f"Error updating courses data table: {e}")


