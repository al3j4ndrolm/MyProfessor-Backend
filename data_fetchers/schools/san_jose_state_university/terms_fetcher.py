# This file contains the code to fetch the terms from the San Jose State University website

# Standard library imports
from bs4 import BeautifulSoup, Tag

# Local imports
import helpers.soup_getter
import logging
from data_fetchers.schools.san_jose_state_university.school_config import SAN_JOSE_STATE_UNIVERSITY_BASE_URL
from data_fetchers.api.terms.configs import TERM_NAME_KEY, TERM_CODE_KEY
from data_fetchers.api.terms.response import create_response_data

logger = logging.getLogger(__name__)

def fetch_terms() -> list[dict]:
    """
    Fetch the terms for San Jose State University.

    Returns [] if the terms fieldset is not found in the soup.
    """

    try:
        logger.info("Fetching terms for San Jose State University")
        soup = helpers.soup_getter.html_url_to_soup(SAN_JOSE_STATE_UNIVERSITY_BASE_URL)

        terms_fieldset = locate_terms_fieldset_in_soup(soup)
        terms_options = locate_terms_options_in_fieldset(terms_fieldset)
        terms_data = build_term_data_list(terms_options)
        logger.info(f"Fetched {len(terms_data)} terms for San Jose State University")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for San Jose State University: {e}")
        return []

def locate_terms_fieldset_in_soup(soup) -> Tag:
    """
    Locate the terms fieldset in the soup.

    Example of soup:
    <html>
        <ul class="nested vertical menu">
            <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
            <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
        </ul>
    </html>

    Raises:
        ValueError: If the terms fieldset is not found in the soup.
    """
    terms_fieldset = soup.find("ul", class_="nested vertical menu")

    if terms_fieldset is None:
        logger.error("Terms fieldset not found in soup")
        raise ValueError("Terms fieldset not found in soup")
    
    return terms_fieldset

def locate_terms_options_in_fieldset(terms_fieldset) -> list[Tag]:
    """
    Locate the terms options in the terms fieldset.

    Example of terms_fieldset:
    <ul class="nested vertical menu">
        <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
        <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
    </ul>

    Raises:
        ValueError: If the terms options are not found in the fieldset.
    """
    
    terms_options = terms_fieldset.find_all("a")[0:2]

    if terms_options is None:
        logger.error("Terms options not found in fieldset")
        raise ValueError("Terms options not found in fieldset")

    return terms_options


def build_term_data_list(terms_options) -> list[dict]:
    """
    Build the term data list.

    Example of terms_options:
    <ul class="nested vertical menu">
        <li><a href="/schedule/2025-2026/fall">Fall 2025</a></li>
        <li><a href="/schedule/2025-2026/winter">Winter 2025</a></li>
    </ul>
    """

    term_data_list = []
    for term in terms_options:

        try:
            value = term.get("href").split("/")[-1]
        except Exception as e:
            logger.error(f"Error getting value from term: {e}")
            raise e

        term_data = create_response_data(term.text, value)
        term_data_list.append(term_data)

    return term_data_list

if __name__ == "__main__":
    print(fetch_terms())