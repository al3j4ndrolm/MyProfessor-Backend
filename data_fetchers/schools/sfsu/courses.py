# Standard library imports
from logger import logger

# Third Party Imports
import time, requests
from bs4 import BeautifulSoup

# we are going to pass the session data and the courses set to update
def update_courses_set_per_term(session_data: dict, courses_set: set, department_code: str) -> set:
    
    try:
        for row in session_data["aaData"]:
            # row[0] is the <a>HTML, row[1] = Type, row[2] = Title, etc.
            soup = BeautifulSoup(row[0], "html.parser")
            a    = soup.find("a")
            course_code = a.text.strip().split(" [")[0]
            course_code = course_code.replace(department_code, department_code.replace(" ", ""))
            course_name = row[2]
            courses_set.add(course_code + " - " + course_name)
    except Exception as e:
        logger.error(f"Error getting data for {session_data}: {e}")
    
    return courses_set
