import pytest
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup, Tag

# Import the module to test
from data_fetchers.schools.de_anza_college.terms_fetcher import (
    fetch_terms,
    locate_term_options_in_soup,
    build_term_data_list
)

class TestTermsFetcher:
    """Test cases for the terms fetcher module."""

    def test_locate_term_options_in_soup(self):
        """Test locating term options in soup using real HTML sample."""
        # Load real HTML sample
        sample_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'test_samples', 'de_anza_college', 'schedule_of_classes.html'
        )
        
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Call the function
        result = locate_term_options_in_soup(soup)
        
        # Assertions based on real HTML content
        assert len(result) == 2  # Real HTML has 2 terms: Summer 2025 and Fall 2025
        assert all(isinstance(option, Tag) for option in result)
        assert result[0].text == "Summer 2025"
        assert result[0].get("value") == "M2025"
        assert result[1].text == "Fall 2025"
        assert result[1].get("value") == "F2025"

    def test_locate_term_options_in_soup_no_fieldset(self):
        """Test when fieldset is not found."""
        html = "<div>No fieldset here</div>"
        soup = BeautifulSoup(html, 'html.parser')
        
        with pytest.raises(AttributeError):
            locate_term_options_in_soup(soup)

    def test_fetch_terms_integration(self):
        """Integration test with real HTML parsing."""
        # Load real HTML sample
        sample_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'test_samples', 'de_anza_college', 'schedule_of_classes.html'
        )
        
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test the full flow
        options = locate_term_options_in_soup(soup)
        data = build_term_data_list(options)
        
        # Assertions based on real HTML content
        assert len(data) == 2
        assert data[0]["term_name"] == "Summer 2025"
        assert data[0]["term_code"] == "M2025"
        assert data[1]["term_name"] == "Fall 2025"
        assert data[1]["term_code"] == "F2025"


if __name__ == "__main__":
    pytest.main([__file__]) 