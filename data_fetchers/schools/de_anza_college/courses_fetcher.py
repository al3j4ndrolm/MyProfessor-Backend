# Standard library imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import json

# Third Party Imports
from bs4 import BeautifulSoup, Tag

# Local Imports
from helpers.soup_getter import html_url_to_soup
from data_fetchers.api.courses.response import create_courses_data
from data_fetchers.schools.de_anza_college.school_config import DEPARTMENTS_BASE_URL, COURSES_BASE_URL
from data_fetchers.schools.de_anza_college.terms_fetcher import fetch_terms
import logging

logger = logging.getLogger(__name__)

def fetch_courses() -> dict:
    """
    Example of return value:
    {
        "ACCT - Accounting": [
            "ACCT 64 - Payroll and Business Tax Accounting",
            "ACCT 1C - Managerial Accounting",
            "ACCT 58 - Auditing",
            "ACCT 67 - Individual Income Taxation",
            ...
        ],
        "BIO - Biology": [
            "BIO 10 - Introduction to Biology",
            "BIO 11 - Introduction to Biology Lab",
            "BIO 12 - Introduction to Biology Lab",
            ...
        ],
        ...
    }
    """

    soup = html_url_to_soup(DEPARTMENTS_BASE_URL)
    departments_full_name_list = extract_departments_full_name_list_with_code_from_soup(soup)
    departments_and_courses_data_table = build_departments_data_table(departments_full_name_list)
    return departments_and_courses_data_table

def extract_departments_full_name_list_with_code_from_soup(soup: BeautifulSoup) -> list:
    """
    Example of return value:
    [
        ("ACCT - Accounting", "ACCT"),
        ("BIO - Biology", "BIO"),
        ...
    ]   
    """

    departments_elements = get_departments_elements_from_soup(soup)
    departments_full_name_list_with_code = []

    for department_element in departments_elements:
        departments_full_name_list_with_code.append((department_element.text, department_element.get("value")))

    return departments_full_name_list_with_code

def build_departments_data_table(departments_full_name_list: list) -> dict:
    """
    Example of return value:
    {
        "ACCT - Accounting": [
            "ACCT 64 - Payroll and Business Tax Accounting",
            "ACCT 1C - Managerial Accounting",
            "ACCT 58 - Auditing",   
            ...
        ],
        "BIO - Biology": [
            "BIO 10 - Introduction to Biology",
            "BIO 11 - Introduction to Biology Lab",
            "BIO 12 - Introduction to Biology Lab",
            ...
        ],  
        ...
    }
    """

    offered_terms_list = get_offered_term_codes()
    departments_and_courses_data_table = {}

    for department_full_name, department_code in departments_full_name_list:
        courses_full_name_list = []
        for term_code in offered_terms_list:
            courses_full_name_list += get_courses_full_name_list_from_department_full_name(department_code, term_code)
        departments_and_courses_data_table.update(create_courses_data(department_full_name, courses_full_name_list))

    return departments_and_courses_data_table

def get_departments_elements_from_soup(soup: BeautifulSoup) -> list:
    """
    Example of return value:
    [
        <option value="ACCT">ACCT - Accounting</option>,
        <option value="BIO">BIO - Biology</option>,
        ...
    ]
    """
    departments_elements_holder = soup.find("select", id="dept-select")
    departments_elements = departments_elements_holder.find_all("option")[1:]
    return departments_elements

def get_courses_elements_holder_from_soup(department_code: str, term_code: str) -> list[Tag]:
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

    soup = html_url_to_soup(f"{COURSES_BASE_URL}dept={department_code}&t={term_code}")
    courses_elements_holder = soup.find("table", class_="table table-schedule table-hover mix-container")
    courses_elements = courses_elements_holder.find_all("tr")[1:]
    return courses_elements

def get_offered_term_codes():
    """
    Example of return value:
    [
        "F2025",
        "W2025",
        ...
    ]
    """
    terms_data_table = fetch_terms()
    term_codes_list = []

    for term_data in terms_data_table:
        term_codes_list.append(term_data["termCode"])
    return term_codes_list

def get_course_name_and_code_from_course_element(course_element: Tag) -> tuple[str, str] | tuple[None, None]:
    """
    Example of return value:
    ("ACCT 64", "Payroll and Business Tax Accounting")
    """

    course_data = course_element.find_all("td")

    if len(course_data) > 5: # This is to avoid the case where the course data is a LAB or CLAS
        course_name_element = course_data[4].find("a").text.strip()
    else:
        course_name_element = None

    course_code_element = course_data[1].text.strip()
    return course_code_element, course_name_element

def get_courses_full_name_list_from_department_full_name(department_code: str, term_code: str) -> list:
    """
    Example of return value:
    [
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        ...
    ]
    """
    
    try:
        courses_elements = get_courses_elements_holder_from_soup(department_code, term_code)
    except Exception as e:
        logger.error(f"Error fetching courses for department {department_code} and term {term_code}: {e}")
        return []

    courses_full_name_list = []
    for course_element in courses_elements:
        course_code, course_name = get_course_name_and_code_from_course_element(course_element)
        if course_name is not None and course_code is not None and department_code in course_code and f"{course_code} - {course_name}" not in courses_full_name_list:
            courses_full_name_list.append(f"{course_code} - {course_name}")

    return courses_full_name_list

if __name__ == "__main__":
    print(json.dumps(fetch_courses(), indent=2))

