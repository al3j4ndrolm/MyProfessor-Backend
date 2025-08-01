# Standard library imports
import json
import re
from logger import logger

# Local imports
from helpers.data import data_keys, data_creators
from helpers.soup_getter import parse_html
from data_fetchers.schools.sfsu.school_config import SCHOOL_NAME
from data_fetchers.schools.sfsu.main import get_session_data

def get_classes_per_department(session_data: dict) -> dict:
    """
    Fetch the classes for SF State University.
    """
    try:
        classes_data_table = {}

        for row in session_data["aaData"]:

            course_name = parse_html(row[0]).get_text().strip().split(" [")[0]
            professor_name = parse_html(row[8]).get_text().strip()
            professor_email = None
            professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)
            
            if course_name not in classes_data_table:
                classes_data_table[course_name] = {}

            if professor_identifier not in classes_data_table[course_name]:
                professor_data = data_creators.create_professor_data(email = professor_email)
                classes_data_table[course_name][professor_identifier] = professor_data
            
            class_data = _get_class_data(row)
            classes_data_table[course_name][professor_identifier][data_keys.PROFESSOR_CLASSES_KEY].append(class_data)
        
        return classes_data_table   
    
    except Exception as e:
        logger.error(f"Error getting data for {session_data}: {e}")

def _get_class_data(row: list[str]) -> dict:

    class_crn = row[4]
    availability = row[9] + row[10] #availability is open seats + waitlist seats
    meeting_data = _parse_meeting(row[6])
    class_data = data_creators.create_class_data(class_crn, availability)
    class_data[data_keys.MEETINGS_KEY].append(meeting_data)
    return class_data

def _parse_meeting(html):
    # 1) if raw_html still has \u003C escapes, unescape them:
    html = html.encode("utf-8").decode("unicode_escape")

    # 2) extract days, time, location with error handling
    days_match = re.search(r"col-md-5[^>]*>([^<]+)<", html)
    time_match = re.search(r"col-md-7[^>]*>([^<]+)<", html)
    loc_match = re.search(r"col-md-12[^>]*>([^<]+)<", html)
    
    # Handle cases where regex doesn't match (e.g., online classes)
    days_raw = days_match.group(1).strip() if days_match else ""
    time_raw = time_match.group(1).strip() if time_match else ""
    loc_raw = loc_match.group(1).strip() if loc_match else ""

    # 3) map two-letter day codes → single letters, build Mon–Sun string
    day_keys = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    day_map  = {"Mo":"M","Tu":"T","We":"W","Th":"R","Fr":"F","Sa":"S","Su":"U"}
    days = "".join(day_map[k] if k in days_raw else "·" for k in day_keys)

    # 4) tidy up the time string
    time = time_raw.replace(" ", "").replace("-", "-") if time_raw else ""

    return {
        "tag": "",
        "days":     days,
        "time":     time,
        "location": loc_raw
    }