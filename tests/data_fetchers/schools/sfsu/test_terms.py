import re

import pytest

from data_fetchers.school_data.schools.sfsu import terms
from data_fetchers.school_data.schools.sfsu.school_config import TERMS_BASE_URL
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.base_test import BaseSchoolTest
from tests.data_fetchers.schools.tests_constants import SEASON_CODE_MAP

TERM_NAME_PATTERN = re.compile(
    r"^\s*(" + "|".join(SEASON_CODE_MAP.keys()) + r") (\d{4})\s*$"
)

class TestSFSUTerms(BaseSchoolTest):
    @property
    def school_name(self):
        return "sfsu"

    @property
    def test_type(self):
        return "terms"

    def test_get_terms(self):
        """Test getting terms from the live SFSU class search page"""
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

            assert re.fullmatch(r"\d{4}", term_code), (
                f"termCode '{term_code}' is not a four digit code"
            )

if __name__ == "__main__":
    pytest.main([__file__])
