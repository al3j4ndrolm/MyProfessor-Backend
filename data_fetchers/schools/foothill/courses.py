from bs4 import BeautifulSoup

def get_courses(department_soup: BeautifulSoup) -> list:
    """
    Get the courses from the soup for a department and term.
    Returns a list of course names like 'ACTG 1A - FINANCIAL ACCOUNTING I'.
    """
    courses = []
    # Find all course blocks
    for course_block in department_soup.find_all("div", class_="fh_sched-grid-2-8-2"):
        course_id_tag = course_block.find("h3", class_="fh_course-id")
        course_title_tag = course_block.find("h3", class_="fh_course-head")
        if course_id_tag and course_title_tag:
            course_id = course_id_tag.text.strip()
            course_title = course_title_tag.text.strip()
            courses.append(f"{course_id} - {course_title}")
    return courses


