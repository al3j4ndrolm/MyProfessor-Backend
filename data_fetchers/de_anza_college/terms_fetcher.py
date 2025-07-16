# Standard library imports
from bs4 import BeautifulSoup, Tag

# Local imports
import helpers.soup_getter
import logging

logger = logging.getLogger(__name__)

def fetch_terms_for_de_anza_college() -> list[dict]:
    """
    Fetch the terms for De Anza College.
    """
    logger.info("Fetching terms for De Anza College")
    try:
        school_url = "https://www.deanza.edu/schedule/"
        soup = helpers.soup_getter.html_url_to_soup(school_url)
        terms_fieldset = locate_terms_fieldset_in_soup(soup)
        terms_options = locate_terms_options_in_fieldset(terms_fieldset)
        terms_data = get_refined_terms_data(terms_options)
        logger.info(f"Fetched {len(terms_data)} terms for De Anza College")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for De Anza College: {e}")
        raise e

def locate_terms_fieldset_in_soup(soup) -> Tag:
    """
    Locate the terms fieldset in the soup.
    """
    try:
        logger.info("Locating terms fieldset in soup")
        terms_fieldset = soup.find("fieldset", id="term-select")
        return terms_fieldset
    except Exception as e:
        logger.error(f"Error locating terms fieldset in soup: {e}")
        raise e

def locate_terms_options_in_fieldset(terms_fieldset) -> list[Tag]:
    """
    Locate the terms options in the terms fieldset.
    """
    try:
        logger.info("Locating terms options in fieldset")
        terms_options = terms_fieldset.find_all("button", type="button")
        return terms_options
    except Exception as e:
        logger.error(f"Error locating terms options in fieldset: {e}")
        raise e

def get_refined_terms_data(terms_options) -> list[dict]:
    """
    Get the refined terms data.
    """
    try:
        logger.info("Getting refined terms data")
        terms_data = []
        for term in terms_options:
            term_data = {
                "term_name": term.text,
                "term_code": term.get("value"),
            }
            terms_data.append(term_data)
        return terms_data
    except Exception as e:
        logger.error(f"Error getting refined terms data: {e}")
        raise e

# For testing
if __name__ == "__main__":
    print(fetch_terms_for_de_anza_college())