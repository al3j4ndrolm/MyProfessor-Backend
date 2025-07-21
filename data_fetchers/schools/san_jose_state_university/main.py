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

def main() -> None:

    terms_soup = soup_getter.html_url_to_soup(TERMS_BASE_URL)
    terms_data_table = get_terms(terms_soup)
    # TODO: update terms_data_table to database `schools`

    term_codes = [ term["termCode"] for term in terms_data_table ]

    courses_data_table = {}
    schedules_data_table = {}

    for term_code in term_codes:
        courses_and_schedules_soup = soup_getter.html_url_to_soup(f"{SCHEDULES_BASE_URL}{term_code}")
        courses_data = get_courses(courses_and_schedules_soup, courses_data_table) # TODO: update courses_data_table to database `courses`
        schedules_data = schedules_data_table.update(get_schedules(courses_and_schedules_soup, courses_data_table)) # TODO: update schedules_data_table to database `schedules`
    
    print(courses_data_table)
    print(schedules_data_table)

if __name__ == "__main__":
    main()