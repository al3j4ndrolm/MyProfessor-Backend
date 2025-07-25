# Standard library imports
import logging
import traceback
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_keys, data_creators

logger = logging.getLogger(__name__)

def get_schedules_per_department(soup: BeautifulSoup) -> dict:
    """
    Fetch the schedules for De Anza College.

    Returns {} if the schedules are not found in the soup.
    """
    schedules_holder = soup.find("table", class_="table table-schedule table-hover mix-container")
    if schedules_holder is None:
        return {}

    try:
        schedules_options = schedules_holder.find_all("tr")
        schedule_data_table = build_schedule_data_table(schedules_options[1:])

        logger.info(f"Extracted schedules for {len(schedule_data_table)} courses.")
        return schedule_data_table
    except Exception as e:
        logger.error(f"Error extracting schedules: {traceback.format_exc()}")
        return {}

def build_schedule_data_table(schedule_rows) -> dict:
    courses_data_table = {}
    last_course_name = None
    last_professor_name = None

    for schedule_row in schedule_rows:
        schedule_data = schedule_row.find_all("td")

        if len(schedule_data) > 5:
            """
            Example of schedule_row (first row is the header):

            <td rowspan="2">25051</td>
            <td rowspan="2">PHYS 2A</td>
            <td rowspan="2">02</td>
            <td rowspan="2"><span class="label label-success label-seats">Open</span></td>
            <td>General Physics I</td>
            <td><span class="days">MTWR···</span></td>
            <td>09:30 AM-10:20 AM</td>
            <td>Ronald Francis</a></td>
            <td>S35</td>
            """
            class_crn = schedule_data[0].text
            course_name = schedule_data[1].text
            availability = schedule_data[3].text
            days = schedule_data[5].text
            time = schedule_data[6].text
            professor_name = schedule_data[7].text
            location = schedule_data[8].text

            last_course_name = course_name
            last_professor_name = professor_name

            # If the course name is not in the schedule data list, add it
            if course_name not in courses_data_table:
                courses_data_table[course_name] = {}

            # If the professor name is not in the course name, add the professor name to the course name
            if professor_name not in courses_data_table[course_name]:
                courses_data_table[course_name][professor_name] = data_creators.create_professor_data(False)
                
            professor_data = courses_data_table[course_name][professor_name]
            class_data = data_creators.create_class_data(class_crn, availability)
            meeting_data = data_creators.create_meeting_data(tag = "", days = days, time = time, location = location)
            data_creators.add_meeting_to_class(class_data, meeting_data)
            data_creators.add_class_to_professor(professor_data, class_data)
        
        # If the schedule data is not 9 elements long, add the meeting to the last visited course name and professor name
        else:
            """
            Example of schedule_row (not first row):

            <td><em>LAB</em></td>
            <td><span class="days">M······</span></td>
            <td><em>10:30 AM-01:20 PM</em></td>
            <td></td>
            <td><em>S17</em></td>
            """
            professor_data = courses_data_table[last_course_name][last_professor_name]
            class_data = professor_data[data_keys.CLASSES_KEY][-1]
            tag = schedule_data[0].text.strip()
            meeting_data = data_creators.create_meeting_data(
                tag = "" if tag == "CLAS" else tag,
                days = schedule_data[1].text,
                time = schedule_data[2].text,
                location = schedule_data[4].text
            )
            data_creators.add_meeting_to_class(class_data, meeting_data)

    return courses_data_table
