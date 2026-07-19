from bs4 import BeautifulSoup

from logger import logger


def get_department_data_table(soup: BeautifulSoup) -> dict:
    """
    Returns example:
        {
            "MATH": "Mathematics",
            "CSE": "Computer Science & Engineering",
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

            if not department_code:
                continue

            department_data_table[department_code] = department_name

        logger.info(f"Extracted {len(department_data_table)} departments.")
        return department_data_table

    except Exception as e:
        logger.error(f"Error extracting departments: {e}")
        return {}

def find_department_elements(soup: BeautifulSoup) -> list:
    subject_dropdown = soup.find("select", id="subject")
    if subject_dropdown is None:
        return []

    return subject_dropdown.find_all("option")

def get_department_code(element) -> str:
    return element.get("value", "").strip()

def get_department_name(element) -> str:
    return element.text.strip()
