# Standard library imports
import logging
import traceback
from bs4 import BeautifulSoup, Tag

# Local imports
from helpers.data import data_keys, data_creators, data_parser
from data_fetchers.school_data.schools.ucb.courses import get_courses_elements, get_course_code

logger = logging.getLogger(__name__)

def get_classes_per_department(soup: BeautifulSoup, department_code: str) -> dict:
    """
    Returns:
        Dictionary mapping course codes to professor data with classes
        Example: {
            "COMPSCI 70": {
                "professor_identifier_1": {
                    "professor_data": {...},
                    "classes": [...]
                }
            }
        }
    """
    try:
        class_elements = get_courses_elements(soup)
        classes_data_table = {}

        for class_element in class_elements:
            course_code = get_course_code(class_element)
            if not course_code:
                continue

            class_crn = _get_class_crn(class_element)
            availability = _get_availability(class_element)

            class_data = data_creators.create_class_data(class_crn, availability)
            for days_raw, time_raw, location in _get_meetings(class_element):
                meeting_data = data_creators.create_meeting_data(
                    tag="",
                    days=data_parser.get_normalized_days(days_raw),
                    time=time_raw,
                    location=location,
                )
                class_data[data_keys.MEETINGS_KEY].append(meeting_data)

            if course_code not in classes_data_table:
                classes_data_table[course_code] = {}

            for professor_name in _get_instructor_names(class_element):
                professor_identifier = data_creators.create_professor_identifier(professor_name, None)

                if professor_identifier not in classes_data_table[course_code]:
                    classes_data_table[course_code][professor_identifier] = data_creators.create_professor_data(email=None)

                classes_data_table[course_code][professor_identifier][data_keys.PROFESSOR_CLASSES_KEY].append(class_data)

        logger.info(f"Extracted classes for {len(classes_data_table)} courses.")
        return classes_data_table

    except Exception as e:
        logger.error(f"Error extracting classes: {traceback.format_exc()}")
        return {}

def _get_class_crn(class_element: Tag) -> str:
    section_info = class_element.find("div", class_="st--section-info-wrapper")
    if section_info is None:
        return "N/A"

    number_div = section_info.find("div", class_="st--section-number")
    if number_div is None:
        return "N/A"

    return number_div.get_text().replace("Class #:", "").strip() or "N/A"

def _get_availability(class_element: Tag) -> str:
    seats_div = class_element.find("div", class_="st--seats")
    if seats_div is None:
        return "N/A"

    label = seats_div.find(["p", "strong"])
    return label.get_text().strip() if label else "N/A"

def _get_meetings(class_element: Tag) -> list[tuple[str, str, str]]:
    meetings_container = class_element.find("div", class_="st--meetings")
    if meetings_container is None:
        return []

    meetings = []
    for meeting in meetings_container.find_all("div", class_="st--meeting-details", recursive=False):
        days_raw = _get_field_text(meeting, "st--meeting-days")
        time_raw = _get_field_text(meeting, "st--meeting-time")
        location = _get_field_text(meeting, "st--location")
        meetings.append((days_raw, time_raw, location))

    return meetings

def _get_field_text(meeting: Tag, class_name: str) -> str:
    field = meeting.find("div", class_=class_name)
    if field is None:
        return ""

    for icon in field.find_all("span", class_=lambda c: c and "icon" in c):
        icon.decompose()

    first_line = field.get_text().split("\n")[0]
    return " ".join(first_line.split()).strip()

def _get_instructor_names(class_element: Tag) -> list[str]:
    instructors_div = class_element.find("div", class_="st--instructors")
    if instructors_div is None:
        return ["Staff"]

    for icon in instructors_div.find_all("span", class_="icon"):
        icon.decompose()

    text = instructors_div.get_text().strip()
    names = [name.strip() for name in text.split(",") if name.strip()]

    return names or ["Staff"]
