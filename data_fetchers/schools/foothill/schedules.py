from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_keys, data_creators
from logger import logger

def get_classes_per_department(department_soup: BeautifulSoup) -> dict:
    """
    Fetch the schedules for a given term and department for Foothill College.
    Returns a nested dict in the same format as De Anza College.
    """
    classes_data_table = {}

    try:
        result_soup = department_soup.find("div", id="schedule_results")
        result_elements = result_soup.find_all("div")
        last_course_code = ""

        for result_element in result_elements:
            if result_element.find("div", class_="fh_grid-id"):
                course_id_tag = result_element.find("h3", class_="fh_course-id")
                course_code = course_id_tag.text.strip()
                classes_data_table[course_code] = {}
                last_course_code = course_code
            elif result_element.find("container", class_="fh_sched-wrap"):
                classes_data_table[last_course_code].update(build_classes_per_course(result_element))

    except Exception as e: 
        logger.error(f"Error getting classes per department: {e}")
        return {}

def build_classes_per_course(course_element: BeautifulSoup) -> dict:
    classes_per_course = {}

    availability = None
    class_crn = None
    days = None
    location = None
    professor_name = None
    time = None

    sessid_dates = schedule_wrap.find_all("div", class_="fh_sessid-dates tang")
    if len(sessid_dates) < 5:
        {}

    for sessid_date in sessid_dates:
        if sessid_date.find("strong") and "Course Number" in sessid_date.find("strong").text:
            class_crn = sessid_date.text.split(":")[1].strip()

    availability = sessid_dates[4].text.strip()

    meet_lines = schedule_wrap.find_all("div", class_="meet-td")
    """
    <div class="meet-td" style="float:unset; display:inline-flex; width:23%;"><p style="font-weight:700; margin:unset; text-decoration:none;">Type</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:21%;"><p style="font-weight:bold; margin:unset; text-decoration:none;">Room</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:24%;"><p style="font-weight:bold; margin:unset; text-decoration:none;">Day &amp; Time</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:32%;"><p style="font-weight:bold; margin:unset; text-decoration:none;">Instructor</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:23%;"><p style="margin:unset;">Lecture</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:21%;"><p style="margin:unset;"><a target='_blank' title='Map/Location information' href='/map/locations.html?act=f&room=3206'>3206</a></p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:24%;"><p class="" style="display:block; margin:unset;">MW 10:00 AM-12:15 PM</p></div>
    <div class="meet-td" style="float:unset; display:inline-flex; width:32%;"><p style="margin:unset;"><a href="/directory/profile/torretto_joe.html">TORRETTO, JOE</a></p></div>
    """

    tag = meet_lines[4].text.strip()
    if tag == "Lecture":
        tag = ""
    location = meet_lines[5].text.strip()
    days, time = _get_days_and_time(meet_lines[6].text.strip())

    """
    <a href="/directory/profile/torretto_joe.html">TORRETTO, JOE</a>
    """
    professor_name = meet_lines[7].text.strip()
    professor_link = meet_lines[7].find("a")["href"] if meet_lines[7].find("a") is not None else None
    professor_email = _get_email_from_link(professor_link)
    professor_identifier = data_creators.create_professor_identifier(professor_name, professor_email)

    if professor_identifier not in classes_per_course:
        professor_data = data_creators.create_professor_data(email = professor_email)
        classes_per_course[professor_identifier] = professor_data

    class_data = data_creators.create_class_data(class_crn=class_crn, availability=availability)
    meeting_data = data_creators.create_meeting_data(tag=tag, days=days, time=time, location=location)
    classes_per_course[professor_identifier][data_keys.PROFESSOR_CLASSES_KEY].append(class_data)
    classes_per_course[professor_identifier][data_keys.PROFESSOR_CLASSES_KEY][-1][data_keys.MEETINGS_KEY].append(meeting_data)

    return classes_per_course

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
        time = day_and_time.removesuffix(days).strip()
        return days, time
