# Standard library imports
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators
from school_config import SCHOOL_NAME

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
    # TODO: Implement based on your school's HTML structure

    return []

def get_term_code(term_element) -> str:
    # TODO: Implement based on your school's structure
    
    return ""

def get_term_name(term_element) -> str:
    # TODO: Implement based on your school's structure
    
    return ""
