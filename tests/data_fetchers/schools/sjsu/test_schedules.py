import os
import pytest
from bs4 import BeautifulSoup
import json
from tests import data_verify
from helpers.soup_getter import html_url_to_soup

from data_fetchers.schools.sjsu import schedules
from data_fetchers.schools.sjsu.school_config import SCHEDULES_BASE_URL

# Helper to get sample soup from HTML file
def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'sjsu', 'classes_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

# Helper to get reference data from JSON file
def get_reference_data():
    reference_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'sjsu', 'classes_test_reference.json'
    )
    with open(reference_path, 'r', encoding='utf-8') as f:
        return json.load(f)

class TestSJSUSchedules:
    def test_get_schedules(self):
        soup = get_sample_soup()
        departments = {"ART"}

        result = schedules.get_classes_per_department(soup, departments)
        expected = get_reference_data()
        print(result)

        assert result == expected
        # Verify the data structure
        data_verify.verify_data_structure_classes_all_departments(result)

if __name__ == "__main__":
    pytest.main([__file__]) 