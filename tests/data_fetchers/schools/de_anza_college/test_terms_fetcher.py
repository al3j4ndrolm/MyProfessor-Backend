import pytest
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup, Tag

# Import the module to test
from data_fetchers.schools.de_anza_college.terms_fetcher import (
    fetch_terms,
    locate_terms_fieldset_in_soup,
    locate_terms_options_in_fieldset,
    build_term_data_list
)

class TestTermsFetcher:
    """Test cases for the terms fetcher module."""

    def test_locate_terms_fieldset_in_soup(self):
        """Test locating the fieldset in soup using real HTML sample."""
        sample_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'test_samples', 'de_anza_college', 'terms_fetcher_test_sample.html'
        )
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        assert fieldset is not None
        assert fieldset.name == 'fieldset'
        assert fieldset.get('id') == 'term-select'

    def test_locate_terms_options_in_fieldset(self):
        """Test locating term options in fieldset using real HTML sample."""
        sample_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'test_samples', 'de_anza_college', 'terms_fetcher_test_sample.html'
        )
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        assert len(options) == 2  # Real HTML has 2 terms: Summer 2025 and Fall 2025
        assert all(isinstance(option, Tag) for option in options)
        assert options[0].text == "Summer 2025"
        assert options[0].get("value") == "M2025"
        assert options[1].text == "Fall 2025"
        assert options[1].get("value") == "F2025"

    def test_locate_terms_fieldset_in_soup_no_fieldset(self):
        """Test when fieldset is not found."""
        html = "<div>No fieldset here</div>"
        soup = BeautifulSoup(html, 'html.parser')
        with pytest.raises(ValueError, match="Terms fieldset not found in soup"):
            locate_terms_fieldset_in_soup(soup)

    def test_locate_terms_options_in_fieldset_no_buttons(self):
        """Test when no buttons are found in fieldset."""
        html = "<fieldset id='term-select'></fieldset>"
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        assert options == []

    def test_fetch_terms_integration(self):
        """Integration test with real HTML parsing."""
        sample_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'test_samples', 'de_anza_college', 'terms_fetcher_test_sample.html'
        )
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        data = build_term_data_list(options)
        assert len(data) == 2
        assert data[0]["term_name"] == "Summer 2025"
        assert data[0]["term_code"] == "M2025"
        assert data[1]["term_name"] == "Fall 2025"
        assert data[1]["term_code"] == "F2025"

if __name__ == "__main__":
    pytest.main([__file__]) 