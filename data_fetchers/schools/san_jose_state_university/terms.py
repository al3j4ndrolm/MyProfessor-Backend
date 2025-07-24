# Standard library imports
import logging
from bs4 import BeautifulSoup

# Local imports
from data_fetchers.api.terms.response import create_term_response_data

logger = logging.getLogger(__name__)

def get_terms(soup: BeautifulSoup) -> list[dict]: 
    """
    Fetch the terms for San Jose State University.

    Returns [] if the terms fieldset is not found in the soup.
    """

    try:
        logger.info("Fetching terms for San Jose State University")

        terms_fieldset = soup.find("ul", class_="nested vertical menu")
        terms_options = terms_fieldset.find_all("a")[0:2]
        terms_data = build_term_data_list(terms_options)

        logger.info(f"Fetched {len(terms_data)} terms for San Jose State University")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for San Jose State University: {e}")
        return []

def build_term_data_list(terms_options) -> list[dict]:
    """
    Build the term data list.

    Example of terms_options:
    [
        <a href="/schedule/2025-2026/fall">Fall 2025</a>,
        <a href="/schedule/2025-2026/winter">Winter 2025</a>
    ]
    """

    term_data_list = []
    for term in terms_options:

        value = term.get("href").split("/")[-1]
        term_data = create_term_response_data(term.text, value)
        term_data_list.append(term_data)

    return term_data_list

