import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup, Tag
import os

from data_fetchers.schools.san_jose_state_university.terms_fetcher import (
    fetch_terms,
    locate_terms_fieldset_in_soup,
    locate_terms_options_in_fieldset,
    build_term_data_list
)

class TestSJStateTermsFetcher:
    def test_locate_terms_fieldset_in_soup(self):
        html = '''<html><ul class="nested vertical menu">
            <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
            <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
        </ul></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        assert fieldset is not None
        assert fieldset.name == 'ul'
        assert 'nested' in fieldset.get('class', [])
        assert 'vertical' in fieldset.get('class', [])
        assert 'menu' in fieldset.get('class', [])

    def test_locate_terms_options_in_fieldset(self):
        html = '''<ul class="nested vertical menu">
            <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
            <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
        </ul>'''
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        assert len(options) == 2
        assert all(isinstance(option, Tag) for option in options)
        assert options[0].text == "Fall 2025"
        assert options[0].get("href") == "/schedule/2025-2026/fall"
        assert options[1].text == "Winter 2025"
        assert options[1].get("href") == "/schedule/2025-2026/winter"

    def test_locate_terms_fieldset_in_soup_no_fieldset(self):
        html = "<div>No fieldset here</div>"
        soup = BeautifulSoup(html, 'html.parser')
        with pytest.raises(ValueError, match="Terms fieldset not found in soup"):
            locate_terms_fieldset_in_soup(soup)

    def test_locate_terms_options_in_fieldset_no_links(self):
        html = "<ul class='nested vertical menu'></ul>"
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        assert options == []

    def test_build_term_data_list(self):
        html = '''<ul class="nested vertical menu">
            <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
            <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
        </ul>'''
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        data = build_term_data_list(options)
        assert len(data) == 2
        assert data[0]["term_name"] == "Fall 2025"
        assert data[0]["term_code"] == "fall"
        assert data[1]["term_name"] == "Winter 2025"
        assert data[1]["term_code"] == "winter"

    def test_build_term_data_list_with_missing_href(self):
        html = '''<ul class="nested vertical menu">
            <li><a>Fall 2025</a></li>
        </ul>'''
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        with pytest.raises(Exception):
            build_term_data_list(options)

    @patch('data_fetchers.schools.san_jose_state_university.terms_fetcher.helpers.soup_getter.html_url_to_soup')
    def test_fetch_terms_success(self, mock_soup_getter):
        mock_html = '''<html><ul class="nested vertical menu">
            <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
            <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
        </ul></html>'''
        mock_soup = BeautifulSoup(mock_html, 'html.parser')
        mock_soup_getter.return_value = mock_soup
        terms = fetch_terms()
        assert len(terms) == 2
        assert terms[0]["term_name"] == "Fall 2025"
        assert terms[0]["term_code"] == "fall"
        assert terms[1]["term_name"] == "Winter 2025"
        assert terms[1]["term_code"] == "winter"

    @patch('data_fetchers.schools.san_jose_state_university.terms_fetcher.helpers.soup_getter.html_url_to_soup')
    def test_fetch_terms_no_fieldset(self, mock_soup_getter):
        mock_html = "<div>No fieldset here</div>"
        mock_soup = BeautifulSoup(mock_html, 'html.parser')
        mock_soup_getter.return_value = mock_soup
        terms = fetch_terms()
        assert terms == []

    @patch('data_fetchers.schools.san_jose_state_university.terms_fetcher.helpers.soup_getter.html_url_to_soup')
    def test_fetch_terms_network_error(self, mock_soup_getter):
        mock_soup_getter.side_effect = Exception("Network error")
        terms = fetch_terms()
        assert terms == []

    def test_integration_with_sample_file(self):
        sample_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'test_samples', 'san_jose_state_university', 'terms_fetcher_test_sample.html'
        )
        with open(sample_path, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        fieldset = locate_terms_fieldset_in_soup(soup)
        options = locate_terms_options_in_fieldset(fieldset)
        data = build_term_data_list(options)
        assert isinstance(data, list)
        assert all('term_name' in d and 'term_code' in d for d in data)

if __name__ == "__main__":
    pytest.main([__file__]) 