import os
import pytest
from bs4 import BeautifulSoup
import ast
from helpers.soup_getter import html_url_to_soup

from data_fetchers.schools.sjsu import courses
from data_fetchers.schools.sjsu.school_config import SCHEDULES_BASE_URL

def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'sjsu', 'schedules_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

class TestSJSUCourses:
    def test_get_courses(self):
        soup = html_url_to_soup(SCHEDULES_BASE_URL + "summer-2025.php")
        result = {}
        courses.update_courses_data_table(soup, result)
        # Load reference data from file
        reference_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 'tests', 'test_samples', 'sjsu', 'courses_test_reference.json'
        )
        with open(reference_path, 'r', encoding='utf-8') as f:
            reference_data = ast.literal_eval(f.read())
        # Compare the result with the reference data

        for department, _ in result.items():
            assert result[department] == set(reference_data[department])


if __name__ == "__main__":
    pytest.main([__file__]) 