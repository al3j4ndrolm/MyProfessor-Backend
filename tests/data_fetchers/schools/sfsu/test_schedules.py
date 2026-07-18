import time

import pytest
import requests

from data_fetchers.school_data.schools.sfsu import departments, schedules, terms
from data_fetchers.school_data.schools.sfsu.school_config import (
    SCHEDULES_BASE_URL,
    SCHEDULES_RESULT_JSON_URL,
    TERMS_BASE_URL,
)
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import fetch_first_term_code, fetch_test_department_data_table

class TestSFSUSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "sfsu"

    @property
    def test_type(self):
        return "schedules"

    def test_get_classes_per_department(self):
        """Test getting schedules from the live SFSU class search page"""
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

        result = schedules.get_classes_per_department(session_data, department_code)

        assert isinstance(result, dict)
        assert len(result) > 0
        data_verify.verify_data_structure_classes_per_department(result)

if __name__ == "__main__":
    pytest.main([__file__])
