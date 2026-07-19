import pytest
import requests
from bs4 import BeautifulSoup

from data_fetchers.school_data.schools.ucsc import departments, schedules, terms
from data_fetchers.school_data.schools.ucsc.school_config import (
    RESULTS_PER_PAGE,
    SCHEDULES_BASE_URL,
    TERMS_BASE_URL,
)
from tests import data_verify
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_utils import fetch_first_term_code, fetch_test_department_data_table

_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def _fetch_department_soup(department_code: str, term_code: str) -> BeautifulSoup:
    payload = {
        "action": "results",
        "binds[:term]": term_code,
        "binds[:session_code]": "",
        "binds[:reg_status]": "all",
        "binds[:subject]": department_code,
        "binds[:catalog_nbr_op]": "=",
        "binds[:catalog_nbr]": "",
        "binds[:title]": "",
        "binds[:instr_name_op]": "contains",
        "binds[:instructor]": "",
        "binds[:ge]": "",
        "binds[:crse_units_op]": "=",
        "binds[:crse_units_exact]": "",
        "binds[:days]": "",
        "binds[:times]": "",
        "binds[:acad_career]": "",
        "binds[:asynch]": "A",
        "binds[:hybrid]": "H",
        "binds[:synch]": "S",
        "binds[:person]": "P",
        "rec_start": "0",
        "rec_dur": str(RESULTS_PER_PAGE),
    }
    response = requests.post(SCHEDULES_BASE_URL, data=payload, headers={"User-Agent": _USER_AGENT})
    return BeautifulSoup(response.text, "html.parser")

class TestUCSCSchedules(BaseSchoolTest):
    @property
    def school_name(self):
        return "ucsc"

    @property
    def test_type(self):
        return "schedules"

    def test_get_classes_per_department(self):
        """Test getting schedules from the live UCSC class search page"""
        soup, term_code = fetch_first_term_code(terms, TERMS_BASE_URL)

        department_code = "MATH"
        fetch_test_department_data_table(departments, soup, department_code)

        department_soup = _fetch_department_soup(department_code, term_code)

        result = schedules.get_classes_per_department(department_soup, department_code)

        assert isinstance(result, dict)
        assert len(result) > 0
        data_verify.verify_data_structure_classes_per_department(result)

if __name__ == "__main__":
    pytest.main([__file__])
