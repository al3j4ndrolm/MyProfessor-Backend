import os
import pytest
from bs4 import BeautifulSoup
from data_fetchers.schools.san_jose_state_university import schedules
import json
from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.san_jose_state_university.school_config import SCHEDULES_BASE_URL

# Helper to get sample soup from HTML file
def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'san_jose_state_university', 'schedules_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

# Helper to get reference data from JSON file
def get_reference_data():
    reference_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'san_jose_state_university', 'schedules_test_reference.json'
    )
    with open(reference_path, 'r', encoding='utf-8') as f:
        return json.load(f)

class TestSJSUSchedules:
    def test_get_schedules(self):
        soup = html_url_to_soup(SCHEDULES_BASE_URL + "summer-2025.php")
        departments = {"ART"}
        result = schedules.get_schedules(soup, departments)
        reference_data = get_reference_data()
        # Compare the result with the reference data (by keys and values)
        assert len(result) == len(reference_data)
        for department, courses in result.items():
            assert department in reference_data
            for course, profs in courses.items():
                assert course in reference_data[department]
                for prof, prof_data in profs.items():
                    assert prof in reference_data[department][course]
                    assert prof_data["hasEmail"] == reference_data[department][course][prof]["hasEmail"]
                    assert prof_data["classes"] == reference_data[department][course][prof]["classes"]

if __name__ == "__main__":
    pytest.main([__file__]) 