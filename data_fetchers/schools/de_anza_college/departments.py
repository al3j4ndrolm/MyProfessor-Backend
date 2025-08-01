import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_department_data_table(soup: BeautifulSoup) -> dict:
    """
    Example of return value:
    {
        "ACCT": "Accounting",
        "BIO": "Biology",
        ...
    } 
    """

    try:
        logger.info("Extracting departments ...")

        department_elements_holder = soup.find("select", id="dept-select")
        department_elements = department_elements_holder.find_all("option")[1:]

        department_data_table = {}
        for element in department_elements:

            department_name = " - ".join(element.text.split(" - ")[1:]).strip()
            department_code = element.get("value").strip()
            department_data_table[department_code] = department_name

        logger.info(f"Extracted {len(department_data_table)} departments.")
        return department_data_table
    
    except Exception as e:
        logger.error(f"Error extracting departments: {e}")
        return {}
