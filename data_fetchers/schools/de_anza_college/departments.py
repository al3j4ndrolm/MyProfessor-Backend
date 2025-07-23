import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_departments(soup: BeautifulSoup) -> list:
    """
    Example of return value:
    [
        ("ACCT - Accounting", "ACCT"),
        ("BIO - Biology", "BIO"),
        ...
    ]   
    """

    try:
        logger.info("Extracting departments ...")

        department_elements_holder = soup.find("select", id="dept-select")
        department_elements = department_elements_holder.find_all("option")[1:]
    except Exception as e:
        logger.error(f"Error extracting departments: {e}")
        return []

    department_name_code_list = []
    for element in department_elements:

        department_name = " - ".join(element.text.split(" - ")[1:]).strip()
        department_code = element.get("value").strip()
        department_name_code_list.append([department_name, department_code])

    logger.info(f"Extracted {len(department_name_code_list)} departments.")
    return department_name_code_list
