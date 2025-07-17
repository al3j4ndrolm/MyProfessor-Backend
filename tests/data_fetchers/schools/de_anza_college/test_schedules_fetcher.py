import pytest
import os
import json
from bs4 import BeautifulSoup, Tag
from unittest.mock import patch

from data_fetchers.schools.de_anza_college.schedules_fetcher import (
    locate_schedules_fieldset_in_soup,
    locate_schedules_options_in_fieldset,
    build_schedule_data_list,
    fetch_schedules
)

class TestSchedulesFetcher:
    """Test cases for the schedules fetcher module using real HTML sample."""

    @pytest.fixture(scope="class")
    def soup(self):
        sample_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 'tests', 'test_samples', 'de_anza_college', 'schedules_fetcher_test_sample.html'
        )
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return BeautifulSoup(html, 'html.parser')

    def test_locate_schedules_fieldset_in_soup(self, soup):
        fieldset = locate_schedules_fieldset_in_soup(soup)
        assert fieldset is not None
        if fieldset is not None:
            assert fieldset.name == 'tbody'
            # Check that the parent is the correct table
            assert fieldset.parent is not None
            assert fieldset.parent.name == 'table'
            assert 'table-schedule' in fieldset.parent.get('class', [])

    def test_locate_schedules_options_in_fieldset(self, soup):
        fieldset = locate_schedules_fieldset_in_soup(soup)
        options = locate_schedules_options_in_fieldset(fieldset)
        assert len(options) > 0
        assert all(isinstance(option, Tag) for option in options)
        # Check that at least one row contains PHYS 4A
        found_phys4a = any('PHYS 4A' in ''.join(td.text for td in row.find_all('td')) for row in options)
        assert found_phys4a

    def test_build_schedule_data_list(self, soup):
        fieldset = locate_schedules_fieldset_in_soup(soup)
        options = locate_schedules_options_in_fieldset(fieldset)
        data = build_schedule_data_list(options)
        # Check that PHYS 4A is in the parsed data
        assert 'PHYS 4A' in data
        # Check that at least one professor is present for PHYS 4A
        professors = list(data['PHYS 4A'].keys())
        assert len(professors) > 0
        # Check that the structure contains classes and meetings
        for prof in professors:
            prof_data = data['PHYS 4A'][prof]
            assert 'classes' in prof_data
            for cls in prof_data['classes']:
                assert 'class_crn' in cls
                assert 'meetings' in cls
                assert isinstance(cls['meetings'], list)
                for meeting in cls['meetings']:
                    assert 'tag' in meeting
                    assert 'days' in meeting
                    assert 'time' in meeting
                    assert 'location' in meeting

    @patch('data_fetchers.schools.de_anza_college.schedules_fetcher.helpers.soup_getter.html_url_to_soup')
    def test_fetch_schedules_matches_reference(self, mock_html_url_to_soup, soup):
        """Test that fetch_schedules returns data matching the reference JSON."""
        # Mock the soup_getter to return our test HTML
        mock_html_url_to_soup.return_value = soup
        
        # Call fetch_schedules
        result = fetch_schedules("F2025", "PHYS")
        
        # Verify the result matches the reference data exactly
        # Load the reference data from a JSON file
        reference_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 'tests', 'test_samples', 'de_anza_college', 'schedules_fetcher_test_reference.json'
        )
        with open(reference_path, 'r', encoding='utf-8') as f:
            reference_data = json.load(f)

        assert result == reference_data

if __name__ == "__main__":
    pytest.main([__file__]) 