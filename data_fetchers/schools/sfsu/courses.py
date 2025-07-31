# Standard library imports
from logger import logger

# Third Party Imports
import time, requests
from bs4 import BeautifulSoup

# we are going to pass the session data and the courses set to update
def update_courses_set_per_term(session_data: dict, courses_set: set) -> set:
    
    try:
        for row in session_data["aaData"]:
            # row[0] is the <a>HTML, row[1] = Type, row[2] = Title, etc.
            soup = BeautifulSoup(row[0], "html.parser")
            a    = soup.find("a")
            courses_set.add(a.text.strip().split(" [")[0] + " - " + row[2])
    except Exception as e:
        logger.error(f"Error getting data for {session_data}: {e}")
    
    return courses_set
