# Standard library imports
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators
from data_fetchers.school_data.schools.ucb.school_config import SCHOOL_NAME, MAX_TERMS

from logger import logger

def get_terms(soup: BeautifulSoup) -> list[dict]:
    """
    Returns example:
        [
            {"term_code": "8588", "term_name": "Fall 2026"},
            {"term_code": "8580", "term_name": "Summer Sessions 2026"},
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
    """
    The term facet nests Summer Sessions sub-sessions (12W, A, B, C, ...) inside their
    parent term's <li>. Only the direct child <a> of each top-level <li> is a real term.
    """
    term_list = soup.find("ul", attrs={"data-drupal-facet-id": "term"})
    if term_list is None:
        return []

    terms_elements = []
    for term_item in term_list.find_all("li", recursive=False):
        term_link = term_item.find("a", recursive=False)
        if term_link is not None:
            terms_elements.append(term_link)

    return terms_elements

def get_term_code(term_element) -> str:
    return term_element.get("data-drupal-facet-item-value", "").strip()

def get_term_name(term_element) -> str:
    value_span = term_element.find("span", class_="facet-item__value")
    return value_span.get_text().strip() if value_span else ""
