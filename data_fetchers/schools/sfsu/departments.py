import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

def get_department_data_table(soup: BeautifulSoup) -> dict:
    """
    Get the departments from the soup.
    """
    try:
        logger.debug("Extracting departments from SFSU")

        department_elements_holder = soup.find("div", id="content")
        script_elements = department_elements_holder.find_all("script")
        department_elements = script_elements[2:len(script_elements)-2]

        department_data_table = {}
        for department_element in department_elements:
            department_code = re.search(r'var subjectCode = "(.*?)";', department_element.text).group(1)
            department_name = re.search(r'var subjectDescription = "(.*?)";', department_element.text).group(1)
            department_data_table[department_code] = department_name

        logger.info(f"Extracted {len(department_data_table)} departments.")
        return department_data_table

    except Exception as e:
        logger.error(f"Error extracting departments: {e}")
        return {}