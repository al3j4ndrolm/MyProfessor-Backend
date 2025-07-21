import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_departments(soup: BeautifulSoup) -> list:
    """   
    Example of return value:
    [
        ("Accounting", "ACCT"),
        ("Biology", "BIO"),
        ...
    ]   
    """
    try:
        dept_select = soup.find("select", {"name": "dept", "id": "Dept"})
        department_elements = dept_select.find_all("option")[1:]
    except Exception as e:
        logger.error(f"Error extracting departments from Foothill College: {e}")
        return []

    department_name_code_list = []
    for element in department_elements:
        department_code = element.get("value")
        department_name = element.text.strip()

        # The value format is "CODE|Name", so we need to extract just the code
        if "|" in department_code:
            department_code = department_code.split("|")[0]
        
        department_name_code_list.append((department_name, department_code))
        
    logger.info(f"Extracted {len(department_name_code_list)} departments from Foothill College")
    return department_name_code_list