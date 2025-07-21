import json
import logging
from data_fetchers.schools.san_jose_state_university.school_config import SCHEDULES_BASE_URL
from helpers import soup_getter
from data_fetchers.api.schedules.response import create_class_response_data, create_meeting_data, add_class_to_professor, add_meeting_to_professor
from bs4 import BeautifulSoup, Tag
from data_fetchers.schools.san_jose_state_university.courses import build_courses_data_table

logger = logging.getLogger(__name__)

def get_schedules(term_code: str, department: str, soup: BeautifulSoup):

    try:
        logger.info(f"Getting schedules for {term_code} and {department}")
        schedules_fieldset = get_schedules_fieldset(soup)
        schedules_options = get_schedules_options(schedules_fieldset)
        schedules_data_table = build_schedules_data_table(schedules_options)
        logger.info(f"Fetched {len(schedules_data_table)} schedules for {term_code} and {department}")
        return schedules_data_table

    except Exception as e:
        logger.error(f"Error getting schedules for {term_code} and {department}: {e}")
        return []

def get_schedules_fieldset(soup: BeautifulSoup) -> Tag:

    schedules_holder = soup.find("table", id="classSchedule")

    if schedules_holder is None:
        raise ValueError("Schedules holder not found in soup for San Jose State University")

    return schedules_holder

def get_schedules_options(schedules_fieldset: Tag) -> list[Tag]:

    try:
        schedules_options = schedules_fieldset.find_all("tr")[1:]
    except Exception as e:
        raise ValueError("Schedules options not found in fieldset for San Jose State University")

    return schedules_options

def build_schedules_data_table(schedules_rows: list[Tag]) -> dict:

    courses_data_table = {}

    for schedule_row in schedules_rows:
        schedule_data = schedule_row.find_all("td")

        if len(schedule_data) == 13:
            class_crn = schedule_data[1].text.strip()
            course_name = schedule_data[0].text.strip().split(' (')[0] # This way we only get the course name
            course_title = schedule_data[2].text.strip()
            availability = schedule_data[12].text.strip()
            days = schedule_data[7]
            time = schedule_data[8]
            professor_name = schedule_data[9].text.strip()
            location = schedule_data[10].text.strip()
            tag = "CLAS"

            if days.find("br") is not None: # This is for the case where the days are split into multiple lines (Multiple schedules fo one class)
                lines = [line.strip() for line in days.stripped_strings if line.strip()]
                days = []
                times = []

                i = 0
                while i < len(lines):
                    day = lines[i]
                    time = lines[i+1] if i+1 < len(lines) and ':' in lines[i+1] else None
                    days.append(day.text.strip())
                    times.append(time.text.strip())
                    i += 2 if time else 1
            else:
                days = days.text.strip() # This is for the case where the days are not split into multiple lines (One schedule for one class)
                time = time.text.strip()
        
            courses_data_table = build_courses_data_table(course_name, course_title, courses_data_table)
        
            professor_data = courses_data_table[course_name][professor_name]
            class_data = create_class_response_data(class_crn, availability)
            add_class_to_professor(professor_data, class_data)
            meeting_data = create_meeting_data(tag, days, time, location)
            add_meeting_to_professor(professor_data, meeting_data)
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
    department_code = "MATH"
    term_code = "2025F"
    soup = soup_getter.html_url_to_soup(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}")
    schedules_data_table = get_schedules(term_code, department_code, soup)
    print(json.dumps(schedules_data_table, indent=2))