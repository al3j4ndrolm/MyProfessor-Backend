# Standard library imports
import logging
from bs4 import BeautifulSoup

# Local imports
<<<<<<< Updated upstream:data_fetchers/schools/san_jose_state_university/terms_fetcher.py
import helpers.soup_getter
import logging
from data_fetchers.schools.san_jose_state_university.school_config import TERMS_BASE_URL
from data_fetchers.api.terms.configs import TERM_NAME_KEY, TERM_CODE_KEY
from data_fetchers.api.terms.response import create_terms_response_data
=======
from data_fetchers.api.terms.response import create_term_response_data
>>>>>>> Stashed changes:data_fetchers/schools/san_jose_state_university/terms.py

logger = logging.getLogger(__name__)

def fetch_terms() -> list[dict]:
    """
    Fetch the terms for San Jose State University.

    Returns [] if the terms fieldset is not found in the soup.
    """

    try:
        logger.info("Fetching terms for San Jose State University")

<<<<<<< Updated upstream:data_fetchers/schools/san_jose_state_university/terms_fetcher.py
        soup = helpers.soup_getter.html_url_to_soup(TERMS_BASE_URL)

        terms_fieldset = locate_terms_fieldset_in_soup(soup)
        terms_options = locate_terms_options_in_fieldset(terms_fieldset)
=======
        terms_fieldset = soup.find("ul", class_="nested vertical menu")
        if terms_fieldset is None:
            raise ValueError("Terms fieldset not found in soup")

        terms_options = terms_fieldset.find_all("a")[0:2]
        if terms_options is None:
            raise ValueError("Terms options not found in fieldset")

>>>>>>> Stashed changes:data_fetchers/schools/san_jose_state_university/terms.py
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
<<<<<<< Updated upstream:data_fetchers/schools/san_jose_state_university/terms_fetcher.py

        try:
            value = term.get("href").split("/")[-1]
        except Exception as e:
            logger.error(f"Error getting value from term: {e}")
            raise e

        term_data = create_terms_response_data(term.text, value)
        term_data_list.append(term_data)

    return term_data_list

if __name__ == "__main__":
    print(fetch_terms())
=======
        value = term.get("href").split("/")[-1]
        term_data = create_term_response_data(term.text, value)
        term_data_list.append(term_data)

    return term_data_list
>>>>>>> Stashed changes:data_fetchers/schools/san_jose_state_university/terms.py
