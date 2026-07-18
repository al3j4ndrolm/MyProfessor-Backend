from helpers.data import data_keys
from helpers.soup_getter import html_url_to_soup
from tests.data_fetchers.schools.tests_constants import (
    COMMON_DEPARTMENTS,
    COURSE_ENTRY_PATTERN,
    TEST_DEPARTMENT_CODE,
)

def fetch_first_term_code(terms_module, terms_base_url: str):
    """Fetch the live terms page and return (soup, term_code) for the first listed term"""
    soup = html_url_to_soup(terms_base_url)
    assert soup is not None, f"Failed to fetch terms page at {terms_base_url}"

    terms_data_list = terms_module.get_terms(soup)
    assert len(terms_data_list) > 0
    term_code = terms_data_list[0][data_keys.TERM_CODE_KEY]

    return soup, term_code

def fetch_test_department_data_table(departments_module, soup, department_code: str = TEST_DEPARTMENT_CODE) -> dict:
    """Fetch the department data table and assert the given department code is present"""
    department_data_table = departments_module.get_department_data_table(soup)
    assert department_code in department_data_table
    return department_data_table

def assert_valid_courses_list(result: list) -> None:
    """Assert that a courses list is well-formed: a non-empty list of 'part1 - part2' strings,
    where part1 splits by at least one space into two non-empty strings, and part2 is non-empty"""
    assert isinstance(result, list)
    assert len(result) > 0

    for entry in result:
        assert isinstance(entry, str)

        match = COURSE_ENTRY_PATTERN.match(entry)
        assert match, f"Course entry '{entry}' does not match expected pattern 'part1 - part2'"

        part1, part2 = match.groups()
        part1_tokens = part1.split()
        assert len(part1_tokens) >= 2 and all(part1_tokens), (
            f"'{part1}' is not splittable by at least one space into two non-empty strings"
        )
        assert part2.strip() != "", f"'{part2}' is not a non-empty string"

def assert_valid_department_data_table(result: dict) -> None:
    """Assert that a department data table is well-formed and contains the common departments"""
    assert isinstance(result, dict)
    assert len(result) > 0

    for department_code, department_name in result.items():
        assert isinstance(department_code, str)
        assert len(department_code) <= 4
        assert isinstance(department_name, str) and department_name != ""

    for department_code, department_name in COMMON_DEPARTMENTS.items():
        assert department_code in result, f"Expected common department '{department_code}' not found"
        assert result[department_code] == department_name, (
            f"Expected '{department_code}' to map to '{department_name}', got '{result[department_code]}'"
        )
