# Standard library imports
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from bs4 import BeautifulSoup, Tag
from pprint import pprint

# Local imports
import helpers.soup_getter
import logging
from data_fetchers.schools.de_anza_college.school_config import SCHEDULES_BASE_URL
from data_fetchers.api.schedules.response import create_class_response_data, create_meeting_data, create_professor_response_data, add_class_to_professor, add_meeting_to_professor
from data_fetchers.api.schedules.configs import HAS_EMAIL_KEY, CLASSES_KEY, MEETINGS_KEY

logger = logging.getLogger(__name__)

def fetch_schedules(term_code: str, department: str, soup: BeautifulSoup) -> dict:
    """
    Fetch the schedules for a given term and department.

    Returns {} if the schedules are not found in the soup.
    """
    try:
        logger.info(f"Fetching schedules for {term_code} and {department}")
        schedules_fieldset = get_schedules_fieldset(soup)
        schedules_options = get_schedules_options(schedules_fieldset)
        schedule_data_table = build_schedule_data_table(schedules_options)
        return schedule_data_table

    except Exception as e:
        return {}

def get_schedules_fieldset(soup) -> Tag:
    """
    Locate the schedules fieldset in the soup.

    Example of soup:
    <html>
        <table class="table table-schedule table-hover mix-container">
            <tbody>
                <tr>
                    <td>Schedule 1</td>
                    <td>Schedule 2</td>
                </tr>
            </tbody>
        </table>
    </html>

    Raises:
        ValueError: If the schedules fieldset is not found in the soup.
    """
    schedules_fieldset = soup.find("table", class_="table table-schedule table-hover mix-container").find("tbody")
    if schedules_fieldset is None:
        raise ValueError("Schedules fieldset not found in soup")

    return schedules_fieldset

def get_schedules_options(schedules_fieldset) -> list[Tag]:
    """
    Locate the schedules options in the schedules fieldset.

    Example of Tag:
    <table class="table table-schedule table-hover mix-container">
        <tr>
            <td>Schedule 1</td>
            <td>Schedule 2</td>
        </tr>
    </table>

    Raises:
        ValueError: If the schedules options are not found in the fieldset.

    """
    schedules_options = schedules_fieldset.find_all("tr")

    if schedules_options is None:
        raise ValueError("Schedules options not found in fieldset")

    return schedules_options

def build_schedule_data_table(schedule_rows) -> dict:
    """
    Build the schedule data list.

    Example of schedules_option:
    <tr>
        <td>PHYS 4A</td>
        <td>John Doe</td>
        <td>Open</td>
        <td>MTWR···</td>
        <td>09:30 AM-10:20 AM</td>
        <td>S35</td>
        <td>CLAS</td>
    </tr>

    Example of return value:
    {
        "PHYS 4A": {
            "John Doe": {
                "has_email": False,
                "classes": [
                    {
                        "class_crn": "123456",
                        "meetings": [
                            {
                                "tag": "CLAS",
                                "days": "MTWR···",
                                "time": "09:30 AM-10:20 AM",
                                "location": "S35"  
                            }
                        ]
                    }
                ]
            }
        }
    }
    """

    courses_data_table = {}

    for schedule_row in schedule_rows:

        schedule_data = schedule_row.find_all("td")

        if len(schedule_data) > 5:
            class_crn = schedule_data[0].text
            course_name = schedule_data[1].text
            availability = schedule_data[3].text
            days = schedule_data[5].text
            time = schedule_data[6].text
            professor_name = schedule_data[7].text
            location = schedule_data[8].text
            tag = "CLAS"

            # If the course name is not in the schedule data list, add it
            if course_name not in courses_data_table:
                courses_data_table[course_name] = {}

            # If the professor name is not in the course name, add the professor name to the course name
            if professor_name not in courses_data_table[course_name]:
                courses_data_table[course_name][professor_name] = create_professor_response_data(professor_name, False)
                
            professor_data = courses_data_table[course_name][professor_name]
            class_data = create_class_response_data(class_crn, availability)
            add_class_to_professor(professor_data, class_data)
            meeting_data = create_meeting_data(tag, days, time, location)
            add_meeting_to_professor(professor_data, meeting_data)
        
        # If the schedule data is not 9 elements long, add the meeting to the last visited course name and professor name
        else:
            professor_data = courses_data_table[course_name][professor_name]
            meeting_data = create_meeting_data(
                tag = schedule_data[0].text,
                days = schedule_data[1].text,
                time = schedule_data[2].text,
                location = schedule_data[4].text
            )
            add_meeting_to_professor(professor_data, meeting_data)

    return courses_data_table

if __name__ == "__main__":
    print(json.dumps(fetch_schedules("F2025", "PHYS"), indent=2))