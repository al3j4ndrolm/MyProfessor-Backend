import os
from bs4 import BeautifulSoup
import pytest
import sys

from data_fetchers.schools.de_anza_college import terms

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )

def get_sample_soup():
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', '..', 'tests', 'test_samples', 'de_anza_college', 'terms_test_sample.html'
    )
    with open(sample_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return BeautifulSoup(html, 'html.parser')

class TestDeAnzaTerms:
    def test_get_terms(self):
        soup = get_sample_soup()
        result = terms.get_terms(soup)
        # The expected result is based on the first two <button type="button"> in the fieldset#term-select
        expected = [
            {"termName": "Summer 2025", "termCode": "M2025"},
            {"termName": "Fall 2025", "termCode": "F2025"}
        ]
        assert result == expected

if __name__ == "__main__":
    pytest.main([__file__]) 