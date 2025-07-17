# Standard library imports
from bs4 import BeautifulSoup, Tag

# Local imports
import helpers.soup_getter
import logging
from .school_config import base_url
from data_fetchers.api.terms.configs import TERM_NAME_KEY, TERM_CODE_KEY
from data_fetchers.api.terms.response import create_response_data

logger = logging.getLogger(__name__)

def fetch_terms() -> list[dict]:
    """
    Fetch the terms for De Anza College.

    Returns [] if the terms fieldset is not found in the soup.
    """
    try:
        logger.info("Fetching terms for De Anza College")
        soup = helpers.soup_getter.html_url_to_soup(base_url)

        terms_fieldset = locate_terms_fieldset_in_soup(soup)
        terms_options = locate_terms_options_in_fieldset(terms_fieldset)
        terms_data = build_term_data_list(terms_options)
        logger.info(f"Fetched {len(terms_data)} terms for De Anza College")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for De Anza College: {e}")
        return []


def locate_terms_fieldset_in_soup(soup) -> Tag:
    """
    Locate the terms fieldset in the soup.

    Example of soup:
        <html>
            <fieldset id="term-select">
                <legend>Select Term</legend>
                <div class="btn-group" role="group" aria-label="Term Select">
                    <button type="button" value="F2025">Fall 2025</button>
                    <button type="button" value="W2025">Winter 2025</button>
                </div>
            </fieldset>
        </html>

    Raises:
        ValueError: If the terms fieldset is not found in the soup.
    """
    terms_fieldset = soup.find("fieldset", id="term-select")

    if terms_fieldset is None:
        logger.error("Terms fieldset not found in soup")
        raise ValueError("Terms fieldset not found in soup")

    return terms_fieldset


def locate_terms_options_in_fieldset(terms_fieldset) -> list[Tag]:
    """
    Locate the terms options in the terms fieldset.

    Example of terms_fieldset:
    <fieldset id="term-select">
        <legend>Select Term</legend>
        <div class="btn-group" role="group" aria-label="Term Select">
            <button type="button" value="F2025">Fall 2025</button>
            <button type="button" value="W2025">Winter 2025</button>
        </div>
    </fieldset>

    Raises:
        ValueError: If the terms options are not found in the fieldset.
    """
    terms_options = terms_fieldset.find_all("button", type="button")

    if terms_options is None:
        logger.error("Terms options not found in fieldset")
        raise ValueError("Terms options not found in fieldset")

    return terms_options

def build_term_data_list(terms_options) -> list[dict]:
    """
    Get the refined terms data.

    Example of terms_options:
    [
        <button type="button" value="F2025">Fall 2025</button>,
        <button type="button" value="W2025">Winter 2025</button>,
    ]

    Raises:
        ValueError: If the terms options are not found in the fieldset.
    """
    term_data_list = []
    for term in terms_options:
        try:
            value = term.get("value")
        except Exception as e:
            logger.error(f"Error getting value from term: {e}")
            raise e
        term_data = create_response_data(term.text, value)
        term_data_list.append(term_data)

    return term_data_list

if __name__ == "__main__":
    print(fetch_terms())