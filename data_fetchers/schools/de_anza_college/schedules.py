# Standard library imports
import logging
import traceback
from bs4 import BeautifulSoup, Tag

# Local imports
from helpers.data import data_keys, data_creators
from data_fetchers.schools.de_anza_college.school_config import SCHOOL_NAME

logger = logging.getLogger(__name__)

def get_classes_per_department(soup: BeautifulSoup, department_code: str) -> dict:
    """
    Fetch the classes for De Anza College.

    Returns {} if the classes are not found in the soup.
    """
    schedules_holder = soup.find("table", class_="table table-schedule table-hover mix-container")
    if schedules_holder is None:
        return {}

    try:
        schedules_options = schedules_holder.find_all("tr")
        schedule_data_table = build_classes_data_table(schedules_options[1:], department_code)

        logger.info(f"Extracted classes for {len(schedule_data_table)} courses.")
        return schedule_data_table
    except Exception as e:
        logger.error(f"Error extracting classes: {traceback.format_exc()}")
        return {}

def build_classes_data_table(schedule_rows: list[Tag], department_code: str) -> dict:
    classes_data_table = {}
    last_course_name = None
    last_professor_identifier = None

    for schedule_row in schedule_rows:
        schedule_tags = schedule_row.find_all("td")

        if len(schedule_tags) > 5:
            """
            Example of schedule_row (first row is the header):

            <td rowspan="2">25051</td>
            <td rowspan="2">PHYS 2A</td>
            <td rowspan="2">02</td>
            <td rowspan="2"><span class="label label-success label-seats">Open</span></td>
            <td>General Physics I</td>
            <td><span class="days">MTWR···</span></td>
            <td>09:30 AM-10:20 AM</td>
            <td><a href="/directory/user.html?u=jimenezsamayoaelsa">Elsa Jimenez-Samayoa</a></td>
            <td>S35</td>
            """
            course_code = schedule_tags[1].text
            professor_name = schedule_tags[7].text
            professor_id = schedule_tags[7].find("a")["href"].split("=")[1] if schedule_tags[7].find("a") is not None else None
            professor_email = f"{professor_id}@deanza.edu" if professor_id else None
            professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)

            last_course_code = course_code
            last_professor_identifier = professor_identifier

            # If the course name is not in the schedule data list, add it
            if course_code not in classes_data_table:
                classes_data_table[course_code] = {}

            # If the professor name is not in the course name, add the professor name to the course name
            if professor_identifier not in classes_data_table[course_code]:
                professor_data = data_creators.create_professor_data(email = professor_email)
                classes_data_table[course_code][professor_identifier] = professor_data

            class_data = _get_class_data(schedule_tags)
            classes_data_table[course_code][professor_identifier][data_keys.PROFESSOR_CLASSES_KEY].append(class_data)
        
        else:
            # In case the row is not a class but a meeting, add the meeting to the last visited class
            meeting_data = _get_meeting_data(schedule_tags)

            professor_data = classes_data_table[last_course_code][last_professor_identifier]
            class_data = professor_data[data_keys.PROFESSOR_CLASSES_KEY][-1]
            class_data[data_keys.MEETINGS_KEY].append(meeting_data)

    return classes_data_table

def _get_class_data(schedule_tags: list[Tag]) -> dict:
    """
    Example of schedule_row (first row is the header):

    <td rowspan="2">25051</td>
    <td rowspan="2">PHYS 2A</td>
    <td rowspan="2">02</td>
    <td rowspan="2"><span class="label label-success label-seats">Open</span></td>
    <td>General Physics I</td>
    <td><span class="days">MTWR···</span></td>
    <td>09:30 AM-10:20 AM</td>
    <td><a href="/directory/user.html?u=jimenezsamayoaelsa">Elsa Jimenez-Samayoa</a></td>
    <td>S35</td>
    """
    class_crn = schedule_tags[0].text
    availability = schedule_tags[3].text
    days = schedule_tags[5].text
    time = schedule_tags[6].text
    location = schedule_tags[8].text

    class_data = data_creators.create_class_data(class_crn, availability)
    meeting_data = data_creators.create_meeting_data(tag = "", days = days, time = time, location = location)
    class_data[data_keys.MEETINGS_KEY].append(meeting_data)

    return class_data

def _get_meeting_data(schedule_tags: list[Tag]) -> dict:
    """
    Example of schedule_row (not first row):

    <td><em>LAB</em></td>
    <td><span class="days">M······</span></td>
    <td><em>10:30 AM-01:20 PM</em></td>
    <td></td>
    <td><em>S17</em></td>
    """
    tag = schedule_tags[0].text.strip()
    meeting_data = data_creators.create_meeting_data(
        tag = "" if tag == "CLAS" else tag,
        days = schedule_tags[1].text,
        time = schedule_tags[2].text,
        location = schedule_tags[4].text
    )
    return meeting_data