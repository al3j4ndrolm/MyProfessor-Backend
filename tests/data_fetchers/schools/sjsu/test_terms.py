import re

import pytest

from data_fetchers.school_data.schools.sjsu import terms
from data_fetchers.school_data.schools.sjsu.school_config import TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_constants import SEASON_CODE_MAP

TERM_NAME_PATTERN = re.compile(
    r"^(" + "|".join(SEASON_CODE_MAP.keys()) + r") (\d{4})$"
)

class TestSJSUTerms(BaseSchoolTest):
    @property
    def school_name(self):
        return "sjsu"

    @property
    def test_type(self):
        return "terms"

    def test_get_terms(self):
        """Test getting terms from the live SJSU schedules index page"""
        soup = html_url_to_soup(TERMS_BASE_URL)
        assert soup is not None, f"Failed to fetch terms page at {TERMS_BASE_URL}"

        result = terms.get_terms(soup)

        assert isinstance(result, list)
        assert len(result) > 0

        for item in result:
            assert isinstance(item, dict)
            assert "termName" in item
            assert "termCode" in item

            term_name = item["termName"]
            term_code = item["termCode"]

            match = TERM_NAME_PATTERN.match(term_name)
            assert match, f"termName '{term_name}' does not match expected pattern '<Season> YYYY'"

            season, year = match.groups()
            expected_code = f"{season.lower()}-{year}"
            assert term_code == expected_code, (
                f"termCode '{term_code}' does not match expected code "
                f"'{expected_code}' derived from termName '{term_name}'"
            )

if __name__ == "__main__":
    pytest.main([__file__])
