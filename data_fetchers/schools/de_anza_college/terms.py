# Standard library imports
import logging
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators

logger = logging.getLogger(__name__)

def get_terms(soup: BeautifulSoup) -> list[dict]:
    """
    Fetch the terms for De Anza College.

    Returns [] if the terms fieldset is not found in the soup.
    """
    try:
        logger.debug("Fetching terms for De Anza College")

        terms_fieldset = soup.find("fieldset", id="term-select")
        terms_options = terms_fieldset.find_all("button", type="button")
        terms_data = build_term_data_list(terms_options)
        
        logger.info(f"Fetched {len(terms_data)} terms for De Anza College")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for De Anza College: {e}")
        return []

def build_term_data_list(terms_options) -> list[dict]:
    """
    Get the refined terms data.

    Example of terms_options:
    [
        <button type="button" value="F2025">Fall 2025</button>,
        <button type="button" value="W2025">Winter 2025</button>,
    ]
    """
    term_data_list = []
    for term in terms_options:
        value = term.get("value")
        term_data = data_creators.create_term_data(term.text, value)
        term_data_list.append(term_data)

    return data_creators.process_term_data_list(term_data_list)