# Standard library imports
import re
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators
from data_fetchers.school_data.ccsf.school_config import SCHOOL_NAME

from logger import logger

def get_terms(soup: BeautifulSoup) -> list[dict]:
    """
    Returns example:
        [
            {"term_code": "1", "term_name": "Spring 2024"},
            {"term_code": "2", "term_name": "Fall 2024"},
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
            
            term_data_list.append(data_creators.create_term_data(term_name, term_code))
        
        logger.info(f"Fetched {len(term_data_list)} terms for {SCHOOL_NAME}")
        return data_creators.process_term_data_list(term_data_list)
        
    except Exception as e:
        logger.error(f"Error fetching terms for {SCHOOL_NAME}: {e}")
        return []

def get_terms_elements(soup: BeautifulSoup) -> list:
    terms_holder = soup.find('select', attrs={'name': re.compile(r'^field_term_target_id')})

    if terms_holder is None:
        logger.warning("No terms found in the HTML structure of CCSF")
        return []

    return terms_holder.find_all('option')[1:]

def get_term_code(term_element) -> str:
    return term_element.get('value')

def get_term_name(term_element) -> str:
    return term_element.text.strip()

