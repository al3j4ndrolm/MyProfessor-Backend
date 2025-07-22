import os
import pytest
from bs4 import BeautifulSoup
from data_fetchers.schools.san_jose_state_university import courses
import ast
from helpers.soup_getter import html_url_to_soup
from data_fetchers.schools.san_jose_state_university.school_config import SCHEDULES_BASE_URL

def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'san_jose_state_university', 'schedules_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

class TestSJSUCourses:
    def test_get_courses(self):
        soup = html_url_to_soup(SCHEDULES_BASE_URL + "fall-2025.php")
        courses_data_table = {}
        result = courses.get_courses(soup, courses_data_table)
        # Load reference data from file
        reference_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 'tests', 'test_samples', 'san_jose_state_university', 'courses_test_reference.json'
        )
        with open(reference_path, 'r', encoding='utf-8') as f:
            reference_data = ast.literal_eval(f.read())
        # Compare the result with the reference data
        for department, _ in result.items():
            assert sorted(list(result[department])) == sorted(list(reference_data[department]))

if __name__ == "__main__":
    pytest.main([__file__]) 