import time

import pytest
import requests

from data_fetchers.school_data.schools.sfsu import courses, departments, terms
from data_fetchers.school_data.schools.sfsu.school_config import (
    SCHEDULES_BASE_URL,
    SCHEDULES_RESULT_JSON_URL,
    TERMS_BASE_URL,
)
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import assert_valid_courses_list, fetch_first_term_code, fetch_test_department_data_table

class TestSFSUCourses(BaseSchoolTest):
    @property
    def school_name(self):
        return "sfsu"

    @property
    def test_type(self):
        return "courses"

    def test_update_courses_set_per_term(self):
        """Test getting courses from the live SFSU class search page"""
        soup, term_code = fetch_first_term_code(terms, TERMS_BASE_URL)

        department_code = "MATH"
        fetch_test_department_data_table(departments, soup, department_code)

        session = requests.Session()
        session.get(
            SCHEDULES_BASE_URL,
            params={
                "searchFor": department_code,
                "term": term_code,
                "classCategory": "REG",
            },
        )
        response = session.get(
            SCHEDULES_RESULT_JSON_URL,
            params={"_": int(time.time() * 1000)},
        )
        session_data = response.json()

        courses_set = set()
        courses.update_courses_set_per_term(session_data, courses_set, department_code)

        result = sorted(list(courses_set))
        assert_valid_courses_list(result)

if __name__ == "__main__":
    pytest.main([__file__])
