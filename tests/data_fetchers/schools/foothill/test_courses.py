import pytest

from data_fetchers.school_data.schools.foothill import courses, departments, terms
from data_fetchers.school_data.schools.foothill.school_config import SCHEDULES_BASE_URL, TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import assert_valid_courses_list, fetch_first_term_code, fetch_test_department_data_table

class TestFoothillCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "foothill"

    @property
    def test_type(self):
        return "courses"

    def test_update_courses_data_table(self):
        """Test getting courses from the live Foothill College schedule page"""
        soup, term_code = fetch_first_term_code(terms, TERMS_BASE_URL)

        department_code = "MATH"
        department_data_table = fetch_test_department_data_table(departments, soup, department_code)
        department_full_name = department_data_table[department_code]

        department_url = f"{SCHEDULES_BASE_URL}?dept={department_code}%7C{department_full_name}&Quarter={term_code}"
        department_soup = html_url_to_soup(department_url)
        assert department_soup is not None, f"Failed to fetch schedule page at {department_url}"

        courses_data_table = set()
        courses.update_courses_data_table(department_soup, courses_data_table)

        result = sorted(list(courses_data_table))
        assert_valid_courses_list(result)

if __name__ == "__main__":
    pytest.main([__file__])
