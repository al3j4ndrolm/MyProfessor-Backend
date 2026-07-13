# Standard library imports
import os, sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Local imports
from bs4 import BeautifulSoup, Tag
from helpers.data import data_creators, data_keys
from data_fetchers.school_data.sjsu.school_config import SCHOOL_NAME
import logging

logger = logging.getLogger(__name__)

def get_classes_per_department(soup: BeautifulSoup, departments: set) -> dict:
    """
    Fetch the schedules for San Jose State University.

    Returns {} if the schedules are not found in the soup.
    """
    logger.debug("Extracting schedules for San Jose State University ...")
    
    try:
        schedules_holder = soup.find("table", id="classSchedule")
        schedules_options = schedules_holder.find_all("tr")[1:]
        classes_data_table = build_classes_data_table(schedules_options, departments)

        logger.info(f"Extracted schedules for {len(classes_data_table)} departments.")
        return classes_data_table
    except Exception as e:
        logger.error(f"Error getting schedules for San Jose State University: {traceback.format_exc()}")
        return {}

def build_classes_data_table(schedules_rows: list[Tag], departments: set) -> dict:

    classes_data_table = {department: {} for department in departments}

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
            location = schedule_data[10]
            professor_name = schedule_data[9].find("a").text.strip() if schedule_data[9].find("a") is not None else schedule_data[9].text.strip()
            professor_email = schedule_data[9].find("a")["href"].split(":")[1] if schedule_data[9].find("a") is not None else None

            department = course_name.split(' ')[0]
            if department not in departments:
                continue

            class_data = data_creators.create_class_data(class_crn, availability)
        
            if days.find("br") is None:
                meeting_data = data_creators.create_meeting_data(
                    tag = "", 
                    days = days.text, 
                    time = time.text, 
                    location = location.text)
                class_data[data_keys.MEETINGS_KEY].append(meeting_data)
            else:
                lines = [line for line in time.get_text(separator='\n').split('\n') if line.strip()]
                days = lines[::2]   # every 0,2,4... line is a day
                time = lines[1::2]

                locations = location.get_text(separator='\n').split('\n')

                for i in range(len(days)):
                    days_per_meeting = "" if days[i] == "TBA" else days[i]
                    time_per_meeting = "" if time[i] == "TBA" else time[i]
                    location_per_meeting = "" if locations[i] == "TBA" else locations[i]
                    meeting_data = data_creators.create_meeting_data(tag = "", days = days_per_meeting, time = time_per_meeting, location = location_per_meeting)
                    class_data[data_keys.MEETINGS_KEY].append(meeting_data)

        if course_name not in classes_data_table[department]:
            classes_data_table[department][course_name] = {}

        professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)
        if professor_identifier not in classes_data_table[department][course_name]:
            professor_data = data_creators.create_professor_data(email = professor_email)
            classes_data_table[department][course_name][professor_identifier] = professor_data

        classes_data_table[department][course_name][professor_identifier][data_keys.PROFESSOR_CLASSES_KEY].append(class_data)

    return classes_data_table
