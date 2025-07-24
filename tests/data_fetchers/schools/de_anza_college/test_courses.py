import os
from bs4 import BeautifulSoup
import pytest
import sys
import json

from data_fetchers.schools.de_anza_college import courses

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'de_anza_college', 'schedules_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

def get_reference_data():
    reference_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'de_anza_college', 'courses_test_reference.json'
    )
    with open(reference_path, 'r', encoding='utf-8') as f:
        return set(json.load(f))

class TestDeAnzaCourses:
    def test_get_courses_per_department(self):
        soup = get_sample_soup()
        result = courses.get_courses_per_department("PHYS", soup)
        expected = get_reference_data()
        assert result == expected

if __name__ == "__main__":
    pytest.main([__file__]) 