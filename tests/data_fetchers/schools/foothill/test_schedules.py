import pytest

from data_fetchers.school_data.schools.foothill import departments, professors, schedules, terms
from data_fetchers.school_data.schools.foothill.school_config import FACULTY_ALL_URL, SCHEDULES_BASE_URL, TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import fetch_first_term_code, fetch_test_department_data_table

class TestFoothillSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "foothill"

    @property
    def test_type(self):
        return "schedules"

    def test_get_classes_per_department(self):
        """Test getting schedules from the live Foothill College schedule page"""
        soup, term_code = fetch_first_term_code(terms, TERMS_BASE_URL)

        department_code = "MATH"
        department_data_table = fetch_test_department_data_table(departments, soup, department_code)
        department_full_name = department_data_table[department_code]

        all_faculty_soup = html_url_to_soup(FACULTY_ALL_URL)
        professor_data_table = professors.get_professor_data_table(all_faculty_soup)

        department_url = f"{SCHEDULES_BASE_URL}?dept={department_code}%7C{department_full_name}&Quarter={term_code}"
        department_soup = html_url_to_soup(department_url)
        assert department_soup is not None, f"Failed to fetch schedule page at {department_url}"

        result = schedules.get_classes_per_department(department_soup, professor_data_table, department_code)

        assert isinstance(result, dict)
        assert len(result) > 0
        data_verify.verify_data_structure_classes_per_department(result)

if __name__ == "__main__":
    pytest.main([__file__])
