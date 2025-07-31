import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

def get_departments(soup: BeautifulSoup) -> list[dict]:
    """
    Get the departments from the soup.
    """
    try:
        logger.debug("Extracting departments from SFSU")

        department_elements_holder = soup.find("div", id="content")
        script_elements = department_elements_holder.find_all("script")
        department_elements = script_elements[2:len(script_elements)-2]

        department_name_code_list = []
        for department_element in department_elements:
            subject_code = re.search(r'var subjectCode = "(.*?)";', department_element.text).group(1)
            subject_description = re.search(r'var subjectDescription = "(.*?)";', department_element.text).group(1)
            department_name_code_list.append((f"{subject_code} - {subject_description}", subject_code))

        return department_name_code_list

    except Exception as e:
        logger.error(f"Error extracting departments: {e}")