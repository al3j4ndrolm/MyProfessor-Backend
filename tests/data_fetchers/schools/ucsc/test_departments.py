import pytest

from data_fetchers.school_data.schools.ucsc import departments
from data_fetchers.school_data.schools.ucsc.school_config import TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_constants import TEST_DEPARTMENT_CODE

class TestUCSCDepartments(BaseSchoolTest):
    @property
    def school_name(self):
        return "ucsc"

    @property
    def test_type(self):
        return "departments"

    def test_get_department_data_table(self):
        """Test getting departments from the live UCSC class search page"""
        soup = html_url_to_soup(TERMS_BASE_URL)
        assert soup is not None, f"Failed to fetch departments page at {TERMS_BASE_URL}"

        result = departments.get_department_data_table(soup)

        assert isinstance(result, dict)
        assert len(result) > 0

        for department_code, department_name in result.items():
            assert isinstance(department_code, str)
            assert len(department_code) <= 4
            assert isinstance(department_name, str) and department_name != ""

        assert TEST_DEPARTMENT_CODE in result

if __name__ == "__main__":
    pytest.main([__file__])
