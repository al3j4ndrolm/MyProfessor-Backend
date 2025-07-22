import sys
import os
import json
import logging
from bs4 import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.san_jose_state_university.terms import get_terms
from data_fetchers.schools.san_jose_state_university.courses import get_courses
from data_fetchers.schools.san_jose_state_university.schedules import get_schedules
from data_fetchers.schools.san_jose_state_university.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL
from helpers import soup_getter

logger = logging.getLogger(__name__)

def main() -> None:

    terms_soup = soup_getter.html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = get_terms(terms_soup)
    # TODO: update terms_data_table to database `schools`

    term_codes = [ term["termCode"] for term in terms_data_table ]
    courses_data_table, schedules_data_table = get_courses_and_schedules(term_codes)
    # TODO: update courses_data_table to database `courses`
    # TODO: update schedules_data_table to database `schedules`


def get_courses_and_schedules(term_codes: list) -> tuple[dict, dict]:
    """
    Example of return schedules_data_table:
    {
        "2025F": {
            "MATH": {
                "MATH 101": {
                    "John Doe": {
                        "has_email": False,
                        "classes": [
                        ]
                    }
                }
            },
            "PHYS": {
                "PHYS 101": {
                    "John Doe": {
                        "has_email": False,
                        "classes": [
                        ]
                    }
                }
            }
        }
    }
    """
    courses_data_table = {}
    schedules_data_table = {}
    departments = set()

    for term_code in term_codes:
        schedules_soup = soup_getter.html_url_to_soup(f"{SCHEDULES_BASE_URL}{term_code}")

        # courses_data includes courses for all departments in one term, is a dict of str to sets
        courses_data = get_courses(schedules_soup, courses_data_table)
        for department, _ in courses_data.items():
            courses_data_table[department].update(courses_data[department])
            departments.add(department)

        # schedules_data includes schedules for all departments in one term
        schedules_data = get_schedules(schedules_soup, departments)
        schedules_data_table[term_code] = schedules_data

    return courses_data_table, schedules_data_table
