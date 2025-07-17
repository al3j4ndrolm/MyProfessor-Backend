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
from data_fetchers.api.terms.response import create_classes_response_data, create_meeting_data
from data_fetchers.api.terms.configs import HAS_EMAIL_KEY, CLASSES_KEY, MEETINGS_KEY

logger = logging.getLogger(__name__)

def fetch_schedules(term_code: str, department: str):
    """
    Fetch the schedules for a given term and department.

    Returns [] if the schedules are not found in the soup.
    """

    try:
        logger.info(f"Fetching schedules for {term_code} and {department}")
        soup = helpers.soup_getter.html_url_to_soup(SCHEDULES_BASE_URL + f"dept={department}&t={term_code}")
        schedules_fieldset = locate_schedules_fieldset_in_soup(soup)
        schedules_options = locate_schedules_options_in_fieldset(schedules_fieldset)
        schedule_data_list = build_schedule_data_list(schedules_options)
        return schedule_data_list

    except Exception as e:
        logger.error(f"Error fetching schedules for {term_code} and {department}: {e}")

def locate_schedules_fieldset_in_soup(soup) -> Tag:
    """
    Locate the schedules fieldset in the soup.

    Example of Tag:
    <table class="table table-schedule table-hover mix-container">

    Raises:
        ValueError: If the schedules fieldset is not found in the soup.
    """
    schedules_fieldset = soup.find("table", class_="table table-schedule table-hover mix-container").find("tbody")
    if schedules_fieldset is None:
        logger.error("Schedules fieldset not found in soup")
        raise ValueError("Schedules fieldset not found in soup")

    return schedules_fieldset

def locate_schedules_options_in_fieldset(schedules_fieldset) -> list[Tag]:
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
        logger.error("Schedules options not found in fieldset")
        raise ValueError("Schedules options not found in fieldset")

    return schedules_options

def build_schedule_data_list(schedules_options):
    """
    Build the schedule data list.

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

    schedule_data_list = {}
    last_visited_course_name = ""
    last_visited_professor_name = ""

    for schedule in schedules_options:

        schedule_data = schedule.find_all("td")
        if len(schedule_data) > 5:

            class_crn = schedule_data[0].text
            course_name = schedule_data[1].text
            availability = schedule_data[3].text
            days = schedule_data[5].text
            time = schedule_data[6].text
            professor_name = schedule_data[7].text
            location = schedule_data[8].text
            tag = "CLAS"

            # If the course name is different from the last visited course name, update the last visited course name and professor name
            if course_name != last_visited_course_name:
                last_visited_course_name = course_name
                last_visited_professor_name = professor_name
            else:
                professor_name = last_visited_professor_name

            # If the course name is not in the schedule data list, add it
            if course_name not in schedule_data_list:
                schedule_data_list[course_name] = {
                    professor_name: {
                        HAS_EMAIL_KEY: False,
                        CLASSES_KEY: [
                            create_classes_response_data(class_crn, availability, days, time, location, tag)
                        ]
                    }
                }
            # If the course name is in the schedule data list, add the professor name to the course name
            elif course_name in schedule_data_list:
                if professor_name not in schedule_data_list[course_name]:
                    schedule_data_list[course_name][professor_name] = {
                        HAS_EMAIL_KEY: False,
                        CLASSES_KEY: [
                            create_classes_response_data(class_crn, availability, days, time, location, tag)
                        ]
                    }
                # If the professor name is in the schedule data list, add the class to the professor name
                else:
                    schedule_data_list[course_name][professor_name][CLASSES_KEY].append(create_classes_response_data(class_crn, availability, days, time, location, tag))
        # If the schedule data is not 9 elements long, add the meeting to the last visited course name and professor name
        else:
            tag = schedule_data[0].text
            days = schedule_data[1].text
            time = schedule_data[2].text
            location = schedule_data[4].text
            schedule_data_list[last_visited_course_name][last_visited_professor_name][CLASSES_KEY][-1][MEETINGS_KEY].append(create_meeting_data(tag, days, time, location))

    return schedule_data_list

if __name__ == "__main__":
    fetch_schedules("F2025", "PHYS")