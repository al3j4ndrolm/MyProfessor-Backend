

# Local Imports
from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.de_anza_college.terms_fetcher import fetch_terms
from data_fetchers.schools.de_anza_college.courses_fetcher import extract_department_name_code_list, get_course_name_list
from data_fetchers.schools.de_anza_college.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL
from data_fetchers.schools.de_anza_college.schedules_fetcher import fetch_schedules
from data_fetchers.api.courses.response import create_courses_data

def main() -> None:
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
    soup = html_url_to_soup(TERMS_BASE_URL)
    departments_full_name_list = extract_department_name_code_list(soup)
    departments_and_courses_data_table = build_departments_data_table(departments_full_name_list, offered_terms_list) # TODO: update to database

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
            soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}dept={department_code}&t={term_code}") 
            fetch_schedules(term_code, department_code, soup) # TODO: update to database
            courses_full_name_list += get_course_name_list(department_code, term_code, soup)

        departments_and_courses_data_table.update(create_courses_data(department_full_name, courses_full_name_list)) # TODO: update to database

    return departments_and_courses_data_table