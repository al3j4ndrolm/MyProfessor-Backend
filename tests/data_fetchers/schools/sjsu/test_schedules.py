import pytest

from data_fetchers.school_data.schools.sjsu import schedules, terms
from data_fetchers.school_data.schools.sjsu.school_config import SCHEDULES_BASE_URL, TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_constants import TEST_DEPARTMENT_CODE
from tests.data_fetchers.schools.tests_utils import fetch_first_term_code

class TestSJSUSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "sjsu"

    @property
    def test_type(self):
        return "schedules"

    def test_get_classes_per_department(self):
        """Test getting schedules from the live SJSU schedule page"""
        _, term_code = fetch_first_term_code(terms, TERMS_BASE_URL)

        schedules_url = f"{SCHEDULES_BASE_URL}{term_code}.php"
        schedules_soup = html_url_to_soup(schedules_url)
        assert schedules_soup is not None, f"Failed to fetch schedule page at {schedules_url}"

        result = schedules.get_classes_per_department(schedules_soup, {TEST_DEPARTMENT_CODE})

        assert isinstance(result, dict)
        assert TEST_DEPARTMENT_CODE in result
        assert len(result[TEST_DEPARTMENT_CODE]) > 0
        data_verify.verify_data_structure_classes_all_departments(result)

if __name__ == "__main__":
    pytest.main([__file__])
