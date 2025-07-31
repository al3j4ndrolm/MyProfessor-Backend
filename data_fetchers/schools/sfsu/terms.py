
from logger import logger
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators

def get_terms(soup: BeautifulSoup) -> list[dict]:
    """
    Get the terms from the soup.

    returns:
    [
        {
            "term_code": "2345",
            "term_name": "Spring 2025"
        },
        ...
    ]
    """
    try:
        logger.debug("Fetching terms for SFSU")

        terms_fieldset = soup.find("div", id="classScheduleQuick_term", class_="radio-label-noindent")
        terms_options = terms_fieldset.find_all("div", class_="radio")
        terms_data = build_term_data_list(terms_options)
        
        logger.info(f"Fetched {len(terms_data)} terms for SFSU")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for SFSU: {e}")
        return []

def build_term_data_list(terms_options) -> list[dict]:
    """
    Build the term data list.
    """
    term_data_list = []
    for term in terms_options:
        term_name = term.text
        term_code = term.find("input").get("value")
        
        term_data = data_creators.create_term_data(term_name, term_code)
        term_data_list.append(term_data)

    return term_data_list