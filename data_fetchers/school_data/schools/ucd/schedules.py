# Standard library imports
import traceback
from bs4 import BeautifulSoup, Tag

# Local imports
from helpers.data import data_keys, data_creators, data_parser
from data_fetchers.school_data.schools.ucd.courses import get_courses_elements, parse_course_row

from logger import logger

# UC Davis lists a "@" CRN with no schedule for course numbers that have no active section this term
_PLACEHOLDER_CRN = "@"

def get_classes_per_department(soup: BeautifulSoup, department_code: str) -> dict:
    """
    Returns:
        Dictionary mapping course codes to professor data with classes
        Example: {
            "ECS 032A": {
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
            course_code, _, _ = parse_course_row(class_element)
            if not course_code:
                continue

            class_crn = _get_class_crn(class_element)
            if not class_crn or class_crn == _PLACEHOLDER_CRN:
                continue

            availability = _get_availability(class_element)
            days_raw, time_raw = _get_days_and_time(class_element)

            meeting_data = data_creators.create_meeting_data(
                tag="",
                days=data_parser.get_normalized_days(days_raw),
                time=time_raw,
                location="",
            )

            if course_code not in classes_data_table:
                classes_data_table[course_code] = {}

            for professor_name in _get_instructor_names(class_element):
                professor_identifier = data_creators.create_professor_identifier(professor_name, None)

                if professor_identifier not in classes_data_table[course_code]:
                    classes_data_table[course_code][professor_identifier] = data_creators.create_professor_data(email=None)

                # UC Davis repeats a section (same CRN) once per meeting pattern (e.g. lecture + discussion),
                # so merge repeats into the existing class's meetings instead of duplicating the class.
                professor_classes = classes_data_table[course_code][professor_identifier][data_keys.PROFESSOR_CLASSES_KEY]
                existing_class_data = next((c for c in professor_classes if c[data_keys.CLASS_CRN_KEY] == class_crn), None)

                if existing_class_data is not None:
                    existing_class_data[data_keys.MEETINGS_KEY].append(meeting_data)
                else:
                    class_data = data_creators.create_class_data(class_crn, availability)
                    class_data[data_keys.MEETINGS_KEY].append(meeting_data)
                    professor_classes.append(class_data)

        logger.info(f"Extracted classes for {len(classes_data_table)} courses.")
        return classes_data_table

    except Exception:
        logger.error(f"Error extracting classes: {traceback.format_exc()}")
        return {}

def _get_class_crn(class_element: Tag) -> str:
    crn_cell = class_element.find("th", attrs={"scope": "row"})
    if crn_cell is None:
        return ""

    return crn_cell.get_text(separator="|", strip=True).split("|")[0].strip()

def _get_availability(class_element: Tag) -> str:
    cells = class_element.find_all("td")
    if len(cells) < 2:
        return "N/A"

    parts = cells[1].get_text(separator="|", strip=True).split("|")
    return parts[1].strip() if len(parts) > 1 else "N/A"

def _get_days_and_time(class_element: Tag) -> tuple[str, str]:
    """
    The CRN cell holds "CRN, e.g. 3:10 - 4:00 PM, MWF" (or just "TBA" for arranged sections).
    """
    crn_cell = class_element.find("th", attrs={"scope": "row"})
    if crn_cell is None:
        return "", ""

    parts = crn_cell.get_text(separator="|", strip=True).split("|")
    if len(parts) < 2:
        return "", ""

    time_days = parts[1].strip()
    time_raw, _, days_raw = time_days.partition(", ")
    return days_raw.strip(), time_raw.strip()

def _get_instructor_names(class_element: Tag) -> list[str]:
    cells = class_element.find_all("td")
    if len(cells) < 4:
        return ["Staff"]

    raw_name = cells[3].get_text(separator="|", strip=True).split("|")[0].strip()
    return [_format_instructor_name(raw_name)] if raw_name else ["Staff"]

def _format_instructor_name(raw_name: str) -> str:
    """
    UC Davis lists instructors as "Last, First Initial" (e.g. "Porquet-Lupine, J").
    Reformats to "First Initial Last" (e.g. "J Porquet-Lupine") for RMP name matching.
    "The Staff" is normalized to "Staff", left unchanged otherwise.
    """
    if raw_name == "The Staff":
        return "Staff"

    if "," not in raw_name:
        return raw_name

    last_name, _, first_initials = raw_name.partition(",")
    first_initials = first_initials.strip()
    last_name = last_name.strip()

    return f"{first_initials} {last_name}".strip() if first_initials else last_name
