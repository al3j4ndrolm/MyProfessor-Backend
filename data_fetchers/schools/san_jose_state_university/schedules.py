# Standard library imports
import os, sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local imports
from bs4 import BeautifulSoup, Tag
from data_fetchers.api.classes.response import create_professor_data, create_class_data, add_class_to_professor, create_meeting_data, add_meeting_to_class
import logging

logger = logging.getLogger(__name__)

def get_schedules_all_departments(soup: BeautifulSoup, departments: set) -> dict:
    """
    Fetch the schedules for San Jose State University.

    Returns {} if the schedules are not found in the soup.
    """
    try:
        schedules_holder = soup.find("table", id="classSchedule")
        if schedules_holder is None:
            raise ValueError("Schedules holder not found in soup for San Jose State University")
        schedules_options = schedules_holder.find_all("tr")[1:]
        if schedules_options is None:
            raise ValueError("Schedules options not found in holder for San Jose State University")
        schedules_data_table = build_schedules_data_table(schedules_options, departments)

        return schedules_data_table

    except Exception as e:
        logger.error(f"Error getting schedules for San Jose State University: {traceback.format_exc()}")
        return {}

def build_schedules_data_table(schedules_rows: list[Tag], departments: set) -> dict:

    schedules_data_table = {department: {} for department in departments}

    for schedule_row in schedules_rows:
        schedule_data = schedule_row.find_all("td")

        if len(schedule_data) > 13:
            """
            Example of schedule_row (first row is the header):
            <td>AAS 1 (Section 01)</td>
            <td>47414</td>
            <td>In Person</td>
            <td>Introduction to Asian American Studies</td>
            <td>GE: 6</td>
            <td> 3.0</td>
            <td>LEC</td>
            <td>MW</td>
            <td>09:00AM-10:15AM</td>
            <td><a href="mailto:joanne.rondilla@sjsu.edu">Joanne Rondilla</a></td>
            <td>DMH355</td>
            <td>08/20/25-12/08/25</td>
            <td>   0</td>
            """

            class_crn = schedule_data[1].text.strip()
            course_name = schedule_data[0].text.strip().split(' (')[0] # This way we only get the course name
            course_title = schedule_data[2].text.strip()
            availability = schedule_data[12].text.strip()
            days = schedule_data[7]
            time = schedule_data[8]
            professor_name = schedule_data[9].text.strip()
            professor_email = schedule_data[9].find("a")["href"].split(":")[1] if schedule_data[9].find("a") is not None else None
            location = schedule_data[10]

            department = course_name.split(' ')[0]
            if department not in departments:
                continue

            class_data = create_class_data(class_crn, availability)
        
            if days.find("br") is None:
                meeting_data = create_meeting_data(
                    tag = "", 
                    days = days.text.strip(), 
                    time = time.text.strip(), 
                    location = location.text.strip())
                add_meeting_to_class(class_data, meeting_data)
            else:
                lines = [line.strip() for line in time.get_text(separator='\n').split('\n') if line.strip()]
                days = lines[::2]   # every 0,2,4... line is a day
                time = lines[1::2]

                locations = location.get_text(separator='\n').split('\n')

                for i in range(len(days)):
                    days_per_meeting = "" if days[i] == "TBA" else days[i]
                    time_per_meeting = "" if time[i] == "TBA" else time[i]
                    location_per_meeting = "" if locations[i] == "TBA" else locations[i]
                    meeting_data = create_meeting_data(tag = "", days = days_per_meeting, time = time_per_meeting, location = location_per_meeting)
                    add_meeting_to_class(class_data, meeting_data)

        if course_name not in schedules_data_table[department]:
            schedules_data_table[department][course_name] = {}

        if professor_name not in schedules_data_table[department][course_name]:
            schedules_data_table[department][course_name][professor_name] = create_professor_data(has_email = professor_email is not None)

        professor_data = schedules_data_table[department][course_name][professor_name]
        add_class_to_professor(professor_data, class_data)

    return schedules_data_table
