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
    # TODO: Implement based on your school's HTML structure
    
    return []

def get_department_code(element) -> str:
    # TODO: Implement based on your school's structure
    
    return ""

def get_department_name(element) -> str:
    # TODO: Implement based on your school's structure
    
    return "" 