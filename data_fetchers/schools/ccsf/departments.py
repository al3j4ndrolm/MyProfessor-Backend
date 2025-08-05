import re
from bs4 import BeautifulSoup

from logger import logger


def get_department_data_table(soup: BeautifulSoup) -> dict:
    """        
    Returns example:
        {
            "MATH": "Mathematics",
            "CS": "Computer Science",
            ...
        }
    """
    try:
        logger.info("Extracting departments ...")

        department_elements = find_department_elements(soup)
        
        if not department_elements:
            logger.warning("No department elements found")
            return {}

        department_data_table = {}
        for element in department_elements:
            department_code = get_department_code(element)
            department_name = get_department_name(element)
            
            department_data_table[department_code] = department_name

        logger.info(f"Extracted {len(department_data_table)} departments.")
        return department_data_table
    
    except Exception as e:
        logger.error(f"Error extracting departments: {e}")
        return {}

def find_department_elements(soup: BeautifulSoup) -> list:
    department_elements = soup.find('select', attrs={'id': re.compile(r'^edit-field-subject-target-id--2')})

    if department_elements is None:
        logger.warning("No department elements found in the HTML structure of CCSF")
        return []
    
    return department_elements.find_all('option')

def get_department_code(element) -> str:
    text = element.text.strip()
    match = re.search(r'\((.*?)\)', text)
    if match:
        return match.group(1)
    return text  # Fallback to full text if no parentheses found

def get_department_name(element) -> str:
    text = element.text.strip()
    match = re.search(r'^(.*?)\s*\(', text)
    if match:
        return match.group(1).strip()
    return text  # Fallback to full text if no parentheses found