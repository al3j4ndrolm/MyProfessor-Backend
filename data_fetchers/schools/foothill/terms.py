# Standard library imports
from bs4 import BeautifulSoup

# Local imports
from helpers.data import data_creators
from logger import logger

def get_terms(soup: BeautifulSoup):
    """
    Extract terms from Foothill College schedule page.
    
    Args:
        soup: BeautifulSoup object of the schedule page
        
    Returns:
        List of dictionaries containing term data with keys:
        - termName: Human readable term name (e.g., "2025 Fall")
        - termCode: Term code used in URLs (e.g., "2025F")
    """
    try:
        logger.info("Extracting terms from Foothill College schedule page")
        
        # Find the Quarter dropdown
        quarter_select = soup.find("select", {"name": "Quarter", "id": "Quarter"})
        
        if not quarter_select:
            logger.error("Quarter dropdown not found in Foothill schedule page")
            return []
        
        # Get all option elements
        term_options = quarter_select.find_all("option")
        
        terms_data = []
        for option in term_options:
            term_code = option.get("value")
            term_name = option.text.strip()
            
            # Skip empty or invalid options
            if not term_code or not term_name:
                continue
                
            term_data = data_creators.create_term_data(term_name, term_code)
            terms_data.append(term_data)
            
        logger.info(f"Extracted {len(terms_data)} terms from Foothill College")
        return data_creators.process_term_data_list(terms_data)
        
    except Exception as e:
        logger.error(f"Error extracting terms from Foothill College: {e}")
        return []
