import os
from bs4 import BeautifulSoup
import pytest
import sys

from data_fetchers.schools.sfsu import terms

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'sfsu', 'terms_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

class TestSFSUTerms:
    def test_get_terms(self):
        soup = get_sample_soup()
        result = terms.get_terms(soup)
        # The expected result is based on the div elements with class="radio" in the fieldset
        expected = [
            {"termName": " Fall 2025", "termCode": "2257"},
            {"termName": " Summer 2025", "termCode": "2255"}
        ]
        assert result == expected

if __name__ == "__main__":
    pytest.main([__file__]) 