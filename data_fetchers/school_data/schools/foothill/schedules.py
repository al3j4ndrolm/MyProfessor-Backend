from bs4 import BeautifulSoup
import traceback

# Local imports
from helpers.data import data_keys, data_creators
from helpers.data import data_parser
from data_fetchers.school_data.schools.foothill.professors import get_professor_email
from logger import logger

def get_classes_per_department(department_soup: BeautifulSoup, professor_data_table: dict, department_code: str) -> dict:
    """
    Fetch the schedules for a given term and department for Foothill College.
    Returns a nested dict in the same format as De Anza College.
    """
    classes_data_table = {}

    try:
        result_soup = department_soup.find("div", id="schedule_results")
        result_elements = result_soup.find_all()
        last_course_code = ""

        for result_element in result_elements:
            # Check if this element is a div with course ID
            if result_element.name == "div" and result_element.find("div", class_="fh_grid-id"):
                course_id_tag = result_element.find("h5", class_="fh_course-id")
                if course_id_tag is None:
                    continue
                course_code = course_id_tag.text.strip()
                classes_data_table[course_code] = {}
                last_course_code = course_code
            # Check if this element is a section with schedule data (skip the empty
            # trailing "end-department fh_sched-wrap" marker div, which has no section head)
            elif (
                result_element.name == "div"
                and result_element.get("class")
                and "fh_sched-wrap" in result_element.get("class")
                and result_element.find("section", class_="fh_section-head")
                and last_course_code
            ):
                update_class_data_for_professor(result_element, classes_data_table[last_course_code], professor_data_table, department_code)
        return classes_data_table

    except Exception:
        logger.error(f"Error getting classes per department: {traceback.format_exc()}")
        return {}

def update_class_data_for_professor(course_element: BeautifulSoup, classes_per_course: dict, professor_data_table: dict, department_code: str) -> None:
    class_crn = None

    sessid_dates = course_element.find_all("div", class_="fh_sessid-dates")
    for sessid_date in sessid_dates:
        label_tag = sessid_date.find("h5")
        crn_tag = sessid_date.find("p")
        if label_tag and crn_tag and "Course Number" in label_tag.text:
            class_crn = crn_tag.text.strip()

    availability_element = course_element.find("div", class_="meet-availability")
    availability = _get_availability(availability_element)
    class_data = data_creators.create_class_data(class_crn=class_crn, availability=availability)

    professor_data = None
    # Meetings live in the first "Type/Room/Day & Time/Instructor" table; a second
    # table (Modality/Textbook/Footnote) follows it, so filter rows by data-label.
    meeting_rows = [
        row for row in course_element.find_all("tr")
        if row.find("td", attrs={"data-label": "Type"}) is not None
    ]

    for meeting_row in meeting_rows:
        professor_identifier, professor_email, meeting_data = _get_meeting_data(meeting_row, professor_data_table, department_code)

        if professor_data is None:
            if professor_identifier not in classes_per_course:
                professor_data = data_creators.create_professor_data(email = professor_email)
                classes_per_course[professor_identifier] = professor_data
            else:
                professor_data = classes_per_course[professor_identifier]
        class_data[data_keys.MEETINGS_KEY].append(meeting_data)

    professor_data[data_keys.PROFESSOR_CLASSES_KEY].append(class_data)
    return

def _get_meeting_data(meeting_row: BeautifulSoup, professor_data_table: dict, department_code: str) -> tuple[str, str, dict]:
    """
    <tr>
    <td data-label="Type">Lecture</td>
    <td data-label="Room"><a ... href='/map/locations.html?act=f&room=4308'>4308</a></td>
    <td data-label="Day &amp; Time">TTh 10:00 AM-11:50 AM</td>
    <td data-label="Instructor">MAZLOOM, BITA</td>
    </tr>
    """
    tag = meeting_row.find("td", attrs={"data-label": "Type"}).text.strip()
    if tag == "Lecture":
        tag = ""
    location = meeting_row.find("td", attrs={"data-label": "Room"}).text.strip()
    days, time = _get_days_and_time(meeting_row.find("td", attrs={"data-label": "Day & Time"}).text.strip())

    # Instructor is plain text; the site no longer links to a profile page with an email, so
    # the email is looked up from the department directory page instead.
    professor_name = meeting_row.find("td", attrs={"data-label": "Instructor"}).text.strip()
    professor_email = get_professor_email(professor_data_table, professor_name, department_code)
    professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)
    return professor_identifier, professor_email, data_creators.create_meeting_data(tag=tag, days=days, time=time, location=location)

def _get_availability(availability_element: BeautifulSoup) -> str:
    """
    <span style="font-weight: normal;">34 of 40 seats open<br>15 of 15 waitlist seats open</span>
    """
    try:
        # Get the text content and split by <br> tags
        availability_text = availability_element.get_text(separator='<br>')
        parts = availability_text.split('<br>')
        
        result_parts = {}
        
        for part in parts:
            part = part.strip()
            if "waitlist seats open" in part:
                # Extract numbers from "15 of 15 waitlist seats open"
                part = part.replace("waitlist seats open", "")
                part = part.replace("of", "/")
                part = part.replace(" ", "")
                result_parts["waitlist_seats"] = part
            elif "seats open" in part:
                # Extract numbers from "34 of 40 seats open"
                part = part.replace("seats open", "")
                part = part.replace("of", "/")
                part = part.replace(" ", "")
                result_parts["seats"] = part
        
        return f"{result_parts['seats']} {result_parts['waitlist_seats']}"
    
    except Exception as e:
        logger.error(f"Error parsing availability: {e}")
        return "Unknown"

def _get_days_and_time(day_and_time: str) -> tuple[str, str]:
    if day_and_time.startswith("TBA"):
        return "", "TBA"
    else:
        days = day_and_time.split(" ")[0]
        normalized_days = data_parser.get_normalized_days(days)
        time = day_and_time.replace(days, "").replace(" ", "")
        return normalized_days, time
