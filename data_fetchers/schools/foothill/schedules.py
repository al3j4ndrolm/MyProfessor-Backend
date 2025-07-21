from bs4 import BeautifulSoup
from data_fetchers.api.schedules.response import (
    create_class_response_data,
    create_meeting_data,
    create_professor_response_data,
    add_class_to_professor,
    add_meeting_to_professor,
)

def get_schedules(soup: BeautifulSoup) -> dict:
    """
    Fetch the schedules for a given term and department for Foothill College.
    Returns a nested dict in the same format as De Anza College.
    """
    schedules_data = {}

    for schedule_wrap in soup.find_all("container", class_="fh_sched-wrap"):

        availability = None
        class_crn = None
        course_code = None
        days = None
        location = None
        professor_name = None
        time = None
        tag = None

        sessid_dates = schedule_wrap.find_all("div", class_="fh_sessid-dates tang")
        if len(sessid_dates) < 5:
            continue

        for sessid_date in sessid_dates:
            if sessid_date.find("strong") and "Section" in sessid_date.find("strong").text:
                course_code = sessid_date.text.split("-")[0]
            if sessid_date.find("strong") and "Course Number" in sessid_date.find("strong").text:
                class_crn = sessid_date.text.split(":")[1].strip()

        availability = sessid_dates[4].text.strip()

        meet_lines = schedule_wrap.find_all("div", class_="meet-td")

        tag = meet_lines[4].text
        location = meet_lines[5].text
        day_and_time = meet_lines[6].text
        professor_name = meet_lines[7].text

        day = day_and_time.split(" ")[0]
        time = day_and_time.split(" ")[1]

        if course_code not in schedules_data:
            schedules_data[course_code] = {}
        if professor_name not in schedules_data[course_code]:
            schedules_data[course_code][professor_name] = create_professor_response_data(professor_name, False)
        professor_data = schedules_data[course_code][professor_name]
        class_data = create_class_response_data(class_crn=class_crn, availability=availability)
        add_class_to_professor(professor_data, class_data)
        meeting_data = create_meeting_data(tag="CLAS", days=days, time=time, location=location)
        add_meeting_to_professor(professor_data, meeting_data)

    return schedules_data



