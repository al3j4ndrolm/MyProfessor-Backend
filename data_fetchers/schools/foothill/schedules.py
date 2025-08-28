from bs4 import BeautifulSoup
import traceback

# Local imports
from helpers.data import data_keys, data_creators
from helpers.data import data_parser
from logger import logger

def get_classes_per_department(department_soup: BeautifulSoup) -> dict:
    """
    Fetch the schedules for a given term and department for Foothill College.
    Returns a nested dict in the same format as De Anza College.
    """
    classes_data_table = {}

    try:
        result_soup = department_soup.find("div", id="schedule_results")
        result_elements = result_soup.find_all()
        last_course_code = ""

        for result_element in result_elements[:-1]:
            # Check if this element is a div with course ID
            if result_element.name == "div" and result_element.find("div", class_="fh_grid-id"):
                course_id_tag = result_element.find("h3", class_="fh_course-id")
                course_code = course_id_tag.text.strip()
                classes_data_table[course_code] = {}
                last_course_code = course_code
            # Check if this element is a container with schedule data
            elif result_element.name == "container" and result_element.get("class") and "fh_sched-wrap" in result_element.get("class"):
                update_class_data_for_professor(result_element, classes_data_table[last_course_code])
        return classes_data_table

    except Exception as e: 
        logger.error(f"Error getting classes per department: {traceback.format_exc()}")
        return {}

def update_class_data_for_professor(course_element: BeautifulSoup, classes_per_course: dict) -> None:
    availability = None
    class_crn = None

    sessid_dates = course_element.find_all("div", class_="fh_sessid-dates tang")
    for sessid_date in sessid_dates:
        if sessid_date.find("strong") and "Course Number" in sessid_date.find("strong").text:
            class_crn = sessid_date.text.split(":")[1].strip()

    availability_element = course_element.find("div", class_="meet-availability")
    availability = _get_availability(availability_element)
    class_data = data_creators.create_class_data(class_crn=class_crn, availability=availability)

    professor_data = None
    meeting_elements = course_element.find_all("div", class_="meet-tr")

    for meeting_element in meeting_elements:
        professor_identifier, meeting_data = _get_meeting_data(meeting_element)

        if professor_data is None:
            if professor_identifier not in classes_per_course:
                professor_data = data_creators.create_professor_data(email = None)
                classes_per_course[professor_identifier] = professor_data
            else:
                professor_data = classes_per_course[professor_identifier]
        class_data[data_keys.MEETINGS_KEY].append(meeting_data)
    
    professor_data[data_keys.PROFESSOR_CLASSES_KEY].append(class_data)
    return

def _get_meeting_data(meeting_element: BeautifulSoup) -> tuple[str, dict]:
    meet_lines = meeting_element.find_all("div", class_="meet-td")
    
    """
    <div class="meet-td" style="float:unset; display:inline-flex; width:23%;"><p style="margin:unset;">Lecture</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:21%;"><p style="margin:unset;"><a target='_blank' title='Map/Location information' href='/map/locations.html?act=f&room=3206'>3206</a></p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:24%;"><p class="" style="display:block; margin:unset;">MW 10:00 AM-12:15 PM</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:32%;"><p style="margin:unset;"><a href="/directory/profile/torretto_joe.html">TORRETTO, JOE</a></p></div>
    """

    tag = meet_lines[0].text.strip()
    if tag == "Lecture":
        tag = ""
    location = meet_lines[1].text.strip()
    days, time = _get_days_and_time(meet_lines[2].text.strip())

    """
    <a href="/directory/profile/torretto_joe.html">TORRETTO, JOE</a>
    """
    professor_name = meet_lines[3].text.strip()
    professor_link = meet_lines[3].find("a")["href"] if meet_lines[3].find("a") is not None else None
    professor_email = _get_email_from_link(professor_link)
    professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)
    return professor_identifier, data_creators.create_meeting_data(tag=tag, days=days, time=time, location=location)

def _get_class_crn(course_element: BeautifulSoup) -> str:
    sessid_dates = course_element.find_all("div", class_="fh_sessid-dates tang")
    for sessid_date in sessid_dates:
        if sessid_date.find("strong") and "Course Number" in sessid_date.find("strong").text:
            class_crn = sessid_date.text.split(":")[1].strip()
            return class_crn
    return "Unknown"

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

def _get_email_from_link(link: str | None) -> str | None:
    # TODO: get email from link https://www.foothill.edu/{link}
    if link is None:
        return None
    return None

def _get_days_and_time(day_and_time: str) -> tuple[str, str]:
    if day_and_time == "TBA":
        return "TBA", "TBA"
    else:
        days = day_and_time.split(" ")[0]
        normalized_days = data_parser.get_normalized_days(days)
        time = day_and_time.replace(days, "").replace(" ", "")
        return normalized_days, time
