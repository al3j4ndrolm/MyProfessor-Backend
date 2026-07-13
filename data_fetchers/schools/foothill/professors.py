# Standard library imports
from bs4 import BeautifulSoup
import traceback

# Local imports
from helpers.data import data_keys
from logger import logger

ALL_DEPARTMENTS_KEY = "all"

def _normalize_name(professor_name: str) -> str:
    """
    Directory pages list names in Title Case ("Ghodrat, Nancy") while schedule
    pages list instructors in ALL CAPS ("GHODRAT, NANCY"), so normalize to a
    single case for lookups/storage in professor_data_table.
    """
    return professor_name.strip().upper()

def get_professor_data_table(soup: BeautifulSoup) -> dict:
    """
    Extract professor names and emails from Foothill College general index page.

    Example of updated table:
    {
        "Ghodrat, Nancy": {
            "all": {
                "email": "ghodratnancy@fhda.edu",
            },
        },
        ...
    }
    """
    professor_data_table = {}

    if soup is None:
        return professor_data_table

    try:
        for row in soup.find_all("tr"):
            email_tag = row.find("a", href=lambda href: href and href.startswith("mailto:"))
            if email_tag is None:
                continue

            cells = row.find_all("td")
            if not cells:
                continue

            professor_name = cells[0].get_text().strip()
            if not professor_name:
                continue

            professor_email = email_tag["href"].split(":", 1)[1].strip()
            if not professor_email:
                continue

            professor_data_table[_normalize_name(professor_name)] = {
                ALL_DEPARTMENTS_KEY: {
                    data_keys.PROFESSOR_EMAIL_KEY: professor_email,
                },
            }

        return professor_data_table

    except Exception:
        logger.error(f"Error getting professor data table from general index: {traceback.format_exc()}")
        return {}


def update_professor_data_table(soup: BeautifulSoup, department_code: str, professor_data_table: dict):
    """
    Extract professor names and emails from a Foothill College department directory page.

    Example of updated table:
    {
        "Ghodrat, Nancy": {
            "all": {
                "email": "ghodratnancy@fhda.edu",
            },
            "ACCT": {
                "email": "ghodratnancy@fhda.edu",
            },
            ...
        },
        ...
    }
    """
    if soup is None:
        return

    try:
        for row in soup.find_all("tr"):
            email_tag = row.find("a", href=lambda href: href and href.startswith("mailto:"))
            if email_tag is None:
                continue

            cells = row.find_all("td")
            if not cells:
                continue

            professor_name = cells[0].get_text().strip()
            if not professor_name:
                continue

            professor_email = email_tag["href"].split(":", 1)[1].strip()
            if not professor_email:
                continue

            normalized_name = _normalize_name(professor_name)
            if normalized_name not in professor_data_table:
                professor_data_table[normalized_name] = {}

            professor_data_table[normalized_name][department_code] = {
                data_keys.PROFESSOR_EMAIL_KEY: professor_email,
            }

    except Exception:
        logger.error(f"Error updating professor data table for {department_code}: {traceback.format_exc()}")


def get_professor_email(professor_data_table: dict, professor_name: str, department_code: str) -> str | None:
    """
    Look up a professor's email, preferring the department-specific entry
    (department directory pages have more accurate emails) and falling back
    to the "all" entry from the general faculty index.
    """
    professor_entry = professor_data_table.get(_normalize_name(professor_name))
    if not professor_entry:
        return None

    department_data = professor_entry.get(department_code) or professor_entry.get(ALL_DEPARTMENTS_KEY)
    return department_data[data_keys.PROFESSOR_EMAIL_KEY] if department_data else None