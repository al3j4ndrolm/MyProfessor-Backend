import os
import pytest
from bs4 import BeautifulSoup
from data_fetchers.schools.san_jose_state_university import schedules
import json
from tests import data_verify
from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.san_jose_state_university.school_config import SCHEDULES_BASE_URL

# Helper to get sample soup from HTML file
def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'sjsu', 'schedules_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

# Helper to get reference data from JSON file
def get_reference_data():
    reference_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'sjsu', 'schedules_test_reference.json'
    )
    with open(reference_path, 'r', encoding='utf-8') as f:
        return json.load(f)

class TestSJSUSchedules:
    def test_get_schedules(self):
        soup = html_url_to_soup(SCHEDULES_BASE_URL + "summer-2025.php")
        departments = {"ART"}
        result = schedules.get_schedules_all_departments(soup, departments)
        reference_data = get_reference_data()

        # Compare the result with the reference data (by keys and values)
        assert result == reference_data

    def test_verify_data_structure_schedules_all_departments(self):
        soup = get_sample_soup()
        result = schedules.get_schedules_all_departments(soup, {"ART"})

        data_verify.verify_data_structure_schedules_all_departments(result)

if __name__ == "__main__":
    pytest.main([__file__]) 