# Standard library imports
import logging
import re
import traceback
from bs4 import BeautifulSoup, Tag

# Local imports
from helpers.data import data_keys, data_creators, data_parser
from data_fetchers.school_data.schools.ucsc.courses import get_courses_elements, parse_course_header

logger = logging.getLogger(__name__)

def get_classes_per_department(soup: BeautifulSoup, department_code: str) -> dict:
    """
    Returns:
        Dictionary mapping course codes to professor data with classes
        Example: {
            "CSE 3": {
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
            course_code, _, _ = parse_course_header(class_element)
            if not course_code:
                continue

            class_crn = _get_class_crn(class_element)
            availability = _get_availability(class_element)
            days_raw, time_raw = _get_days_and_time(class_element)
            location = _get_location(class_element)

            class_data = data_creators.create_class_data(class_crn, availability)
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
    crn_link = class_element.find("a", id=re.compile(r"^class_nbr_"))
    return crn_link.get_text().strip() if crn_link else "N/A"

def _get_availability(class_element: Tag) -> str:
    availability_text = class_element.find(string=re.compile("Enrolled"))
    return availability_text.strip() if availability_text else "N/A"

def _get_instructor_names(class_element: Tag) -> list[str]:
    icon = class_element.find("i", class_="fa-user")
    if icon is None:
        return []

    container = icon.parent
    raw_names = _clean_field_lines(container)

    instructor_names = []
    for raw_name in raw_names:
        instructor_names.append(_format_instructor_name(raw_name))

    return instructor_names or ["Staff"]

def _get_days_and_time(class_element: Tag) -> tuple[str, str]:
    icon = class_element.find("i", class_="fa-clock-o")
    if icon is None:
        return "", ""

    text = _clean_field(icon.parent)
    days_raw, _, time_raw = text.partition(" ")
    return days_raw.strip(), time_raw.strip()

def _get_location(class_element: Tag) -> str:
    icon = class_element.find("i", class_="fa-location-arrow")
    if icon is None:
        return ""

    return _clean_field(icon.parent)

def _clean_field(container: Tag) -> str:
    for icon in container.find_all("i"):
        icon.decompose()
    return container.get_text(separator=" ").strip()

def _clean_field_lines(container: Tag) -> list[str]:
    for icon in container.find_all("i"):
        icon.decompose()
    return [line.strip() for line in container.get_text(separator="\n").split("\n") if line.strip()]

def _format_instructor_name(raw_name: str) -> str:
    """
    UCSC lists instructors as "Last,First.M." (e.g. "Moulds,G.B.").
    Reformats to "First.M. Last" (e.g. "G.B. Moulds") for RMP name matching, leaving "Staff" untouched.
    """
    if "," not in raw_name:
        return raw_name

    last_name, _, first_initials = raw_name.partition(",")
    first_initials = first_initials.strip()
    last_name = last_name.strip()

    return f"{first_initials} {last_name}".strip() if first_initials else last_name
