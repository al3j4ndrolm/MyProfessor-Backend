# Standard library imports
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Third Party Imports
from bs4 import BeautifulSoup, Tag

# Local Imports
from helpers.soup_getter import html_url_to_soup
from data_fetchers.api.courses.response import create_courses_data
from data_fetchers.schools.de_anza_college.school_config import DEPARTMENTS_BASE_URL, COURSES_BASE_URL
from data_fetchers.schools.de_anza_college.terms_fetcher import fetch_terms
from data_fetchers.schools.de_anza_college.schedules_fetcher import fetch_schedules
import logging

logger = logging.getLogger(__name__)

def fetch_courses() -> dict:
    """
    Example of return value:
    {
        "ACCT - Accounting": [
            "ACCT 64 - Payroll and Business Tax Accounting",
            "ACCT 1C - Managerial Accounting",
            ...
        ],
        "BIO - Biology": [
            "BIO 10 - Introduction to Biology",
            "BIO 11 - Introduction to Biology Lab",
            ...
        ],
        ...
    }
    """
    terms_data_table = fetch_terms()
    offered_terms_list = [ term["termCode"] for term in terms_data_table ]

    soup = html_url_to_soup(DEPARTMENTS_BASE_URL)
    departments_full_name_list = extract_department_name_code_list(soup)
    departments_and_courses_data_table = build_departments_data_table(departments_full_name_list, offered_terms_list)
    return departments_and_courses_data_table

def extract_department_name_code_list(soup: BeautifulSoup) -> list:
    """
    Example of return value:
    [
        ("ACCT - Accounting", "ACCT"),
        ("BIO - Biology", "BIO"),
        ...
    ]   
    """

    try:
        department_elements_holder = soup.find("select", id="dept-select")
        department_elements = department_elements_holder.find_all("option")[1:]
    except Exception as e:
        logger.error(f"Error fetching department elements: {e}")
        return []

    department_name_code_list = []

    for element in department_elements:
        department_name_code_list.append((element.text, element.get("value")))

    return department_name_code_list

def build_departments_data_table(departments_full_name_list: list, offered_terms_list: list) -> dict:
    """
    Example of return value:
    {
        "ACCT - Accounting": [
            "ACCT 64 - Payroll and Business Tax Accounting",
            "ACCT 1C - Managerial Accounting",
            ...
        ],
        "BIO - Biology": [
            "BIO 10 - Introduction to Biology",
            "BIO 11 - Introduction to Biology Lab",
            ...
        ],  
        ...
    }
    """
    
    departments_and_courses_data_table = {}

    for department_full_name, department_code in departments_full_name_list:
        courses_full_name_list = []

        for term_code in offered_terms_list:
            soup = html_url_to_soup(f"{COURSES_BASE_URL}dept={department_code}&t={term_code}") 
            fetch_schedules(term_code, department_code, soup) # TODO: update to database
            courses_full_name_list += get_course_name_list(department_code, term_code, soup)

        departments_and_courses_data_table.update(create_courses_data(department_full_name, courses_full_name_list))

    return departments_and_courses_data_table

def get_course_name_list(department_code: str, term_code: str, soup: BeautifulSoup) -> list:
    """
    Example of return value:
    [
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        ...
    ]
    """

    try:
        courses_elements = get_courses_elements_holder(department_code, term_code, soup)
    except Exception as e:
        return []

    courses_full_name_set = set()
    for course_element in courses_elements:
        course_code, course_name = get_course_name_and_code(course_element)
        if department_code in course_code and course_code and course_name:
            courses_full_name_set.add(f"{course_code} - {course_name}")
        
    return list(courses_full_name_set)

def get_courses_elements_holder(department_code: str, term_code: str, soup: BeautifulSoup) -> list[Tag]:
    """
    Example of return value:
    [
        <tr class="mix">
            <td>ACCT 64</td>
            <td>Payroll and Business Tax Accounting</td>
            ... 
        </tr>,
        ...
    ]
    """
    courses_elements_holder = soup.find("table", class_="table table-schedule table-hover mix-container")
    courses_elements = courses_elements_holder.find_all("tr")[1:]
    return courses_elements

def get_course_name_and_code(course_element: Tag) -> tuple[str, str]:
    """
    Example of return value:
    ("ACCT 64", "Payroll and Business Tax Accounting")
    """

    course_data = course_element.find_all("td")

    if len(course_data) > 5: # This is to avoid the case where the course data is a LAB or CLAS
        course_name = course_data[4].find("a").text.strip()
        course_code = course_data[1].text.strip()
        return course_code, course_name
    else:
        return "", ""

if __name__ == "__main__":
    print(json.dumps(fetch_courses(), indent=2))

