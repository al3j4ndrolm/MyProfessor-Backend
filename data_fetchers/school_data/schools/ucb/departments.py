from bs4 import BeautifulSoup

from logger import logger


def get_department_data_table(soup: BeautifulSoup) -> dict:
    """
    Returns example:
        {
            "5391": "American Studies",
            "5582": "Computer Science",
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
    subject_area_block = soup.find("div", id="block-subjectarea")
    if subject_area_block is None:
        return []

    return subject_area_block.find_all("a", attrs={"data-drupal-facet-item-value": True})

def get_department_code(element) -> str:
    return element.get("data-drupal-facet-item-value", "").strip()

def get_department_name(element) -> str:
    value_span = element.find("span", class_="facet-item__value")
    return value_span.get_text().strip() if value_span else ""
