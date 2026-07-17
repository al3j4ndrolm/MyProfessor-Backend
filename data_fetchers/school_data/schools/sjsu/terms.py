# Standard library imports
import logging
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators

logger = logging.getLogger(__name__)

def get_terms(soup: BeautifulSoup) -> list[dict]: 
    """
    Fetch the terms for San Jose State University.

    Returns [] if the terms fieldset is not found in the soup.
    """

    try:
        logger.debug("Fetching terms for San Jose State University")

        terms_fieldset = soup.find("ul", class_="nested vertical menu")
        terms_options = terms_fieldset.find_all("a")[0:2]
        terms_data = build_term_data_list(terms_options)

        logger.info(f"Fetched {len(terms_data)} terms for San Jose State University")
        return data_creators.process_term_data_list(terms_data)
    except Exception as e:
        logger.error(f"Error fetching terms for San Jose State University: {e}")
        return []

def build_term_data_list(terms_options) -> list[dict]:
    """
    Build the term data list.

    Example of terms_options:
    [
        <a href="/classes/schedules/summer-2025.php" class="gtm-nav--local">Summer 2025</a>,
        <a href="/classes/schedules/fall-2025.php" class="gtm-nav--local">Fall 2025</a>,
    ]
    """

    term_data_list = []
    for term in terms_options:

        term_code = term.get("href").split("/")[-1].strip(".php")
        term_name = term.text

        term_data = data_creators.create_term_data(term_name=term_name, term_code=term_code)
        term_data_list.append(term_data)

    return term_data_list

