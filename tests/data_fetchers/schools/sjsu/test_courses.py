import pytest

from data_fetchers.school_data.schools.sjsu import courses, terms
from data_fetchers.school_data.schools.sjsu.school_config import SCHEDULES_BASE_URL, TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import assert_valid_courses_list, fetch_first_term_code

class TestSJSUCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "sjsu"

    @property
    def test_type(self):
        return "courses"

    def test_update_courses_data_table(self):
        """Test getting courses from the live SJSU schedule page"""
        _, term_code = fetch_first_term_code(terms, TERMS_BASE_URL)

        schedules_url = f"{SCHEDULES_BASE_URL}{term_code}.php"
        schedules_soup = html_url_to_soup(schedules_url)
        assert schedules_soup is not None, f"Failed to fetch schedule page at {schedules_url}"

        courses_data_table = {}
        courses.update_courses_data_table(schedules_soup, courses_data_table)

        department_code = "MATH"
        assert department_code in courses_data_table

        result = sorted(list(courses_data_table[department_code]))
        assert_valid_courses_list(result)

if __name__ == "__main__":
    pytest.main([__file__])
