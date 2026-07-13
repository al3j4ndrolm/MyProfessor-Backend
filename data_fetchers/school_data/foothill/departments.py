from bs4 import BeautifulSoup
from logger import logger

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
        dept_select = soup.find("select", {"name": "dept", "id": "Dept"})
        department_elements = dept_select.find_all("option")[1:]
    except Exception as e:
        logger.error(f"Error extracting departments from Foothill College: {e}")
        return {}

    department_data_table = {}
    for element in department_elements:
        department_code = element.get("value")
        department_name = element.text.strip()

        # The value format is "CODE|Name", so we need to extract just the code
        if "|" in department_code:
            department_code = department_code.split("|")[0]
        
        department_data_table[department_code] = department_name
        
    logger.info(f"Extracted {len(department_data_table)} departments from Foothill College")
    return department_data_table