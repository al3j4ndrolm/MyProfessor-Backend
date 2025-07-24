import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from helpers.soup_getter import html_url_to_soup
from data_fetchers.api.terms.configs import TERM_CODE_KEY
from data_fetchers.schools.san_jose_state_university.terms import get_terms
from data_fetchers.schools.san_jose_state_university.courses import update_courses_data_table
from data_fetchers.schools.san_jose_state_university.schedules import get_schedules_all_departments
from data_fetchers.schools.san_jose_state_university.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME
from database.courses import save_courses_data
from database.schedules import save_schedules_data

logger = logging.getLogger(__name__)

def main() -> None:

    terms_soup = html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = get_terms(terms_soup)
    # TODO: update terms_data_table to database `schools`

    term_codes = [ term[TERM_CODE_KEY] for term in terms_data_table ]
    courses_data_table, schedules_data_table = get_courses_and_schedules(term_codes)
    save_courses_data(courses_data_table, SCHOOL_NAME)
    save_schedules_data(schedules_data_table, SCHOOL_NAME)


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
        schedules_soup = html_url_to_soup(f"{SCHEDULES_BASE_URL}{term_code}")

        # courses_data includes courses for all departments in one term, is a dict of str to sets
        update_courses_data_table(schedules_soup, courses_data_table)
        for department, _ in courses_data_table.items():
            departments.add(department)

        # schedules_data includes schedules for all departments in one term
        schedules_data = get_schedules_all_departments(schedules_soup, departments)
        schedules_data_table[term_code] = schedules_data

    return courses_data_table, schedules_data_table