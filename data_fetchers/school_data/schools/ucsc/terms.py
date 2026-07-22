# Standard library imports
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators
from data_fetchers.school_data.schools.ucsc.school_config import SCHOOL_NAME, MAX_TERMS

from logger import logger

def get_terms(soup: BeautifulSoup) -> list[dict]:
    """
    Returns example:
        [
            {"term_code": "2268", "term_name": "2026 Fall Quarter"},
            {"term_code": "2264", "term_name": "2026 Summer Quarter"},
            ...
        ]
    """
    try:
        logger.debug(f"Fetching terms for {SCHOOL_NAME}")

        terms_elements = get_terms_elements(soup)

        if not terms_elements:
            logger.warning("No terms found in the HTML structure")
            return []

        term_data_list = []
        for term_element in terms_elements:
            term_code = get_term_code(term_element)
            term_name = get_term_name(term_element)

            if not term_code:
                continue

            term_data_list.append(data_creators.create_term_data(term_name, term_code))

        processed_term_data_list = data_creators.process_term_data_list(term_data_list)[:MAX_TERMS]

        logger.info(f"Fetched {len(processed_term_data_list)} terms for {SCHOOL_NAME}")
        return processed_term_data_list

    except Exception as e:
        logger.error(f"Error fetching terms for {SCHOOL_NAME}: {e}")
        return []

def get_terms_elements(soup: BeautifulSoup) -> list:
    term_dropdown = soup.find("select", id="term_dropdown")
    if term_dropdown is None:
        return []

    return term_dropdown.find_all("option")

def get_term_code(term_element) -> str:
    return term_element.get("value", "").strip()

def get_term_name(term_element) -> str:
    return term_element.text.strip()
