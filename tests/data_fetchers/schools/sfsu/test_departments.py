import pytest

from data_fetchers.school_data.schools.sfsu import departments
from data_fetchers.school_data.schools.sfsu.school_config import TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import assert_valid_department_data_table

class TestSFSUDepartments(BaseSchoolTest):
    @property
    def school_name(self):
        return "sfsu"

    @property
    def test_type(self):
        return "departments"

    def test_get_department_data_table(self):
        """Test getting departments from the live SFSU class search page"""
        soup = html_url_to_soup(TERMS_BASE_URL)
        assert soup is not None, f"Failed to fetch departments page at {TERMS_BASE_URL}"

        result = departments.get_department_data_table(soup)

        assert_valid_department_data_table(result)

if __name__ == "__main__":
    pytest.main([__file__])
