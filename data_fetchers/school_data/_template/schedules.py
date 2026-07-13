# Standard library imports
import logging
import traceback
from bs4 import BeautifulSoup, Tag

# Local imports
from helpers.data import data_keys, data_creators

logger = logging.getLogger(__name__)

def get_classes_per_department(soup: BeautifulSoup, department_code: str) -> dict:
    """
    Returns:
        Dictionary mapping course codes to professor data with classes
        Example: {
            "MATH 1A": {
                "professor_identifier_1": {
                    "professor_data": {...},
                    "classes": [...]
                }
            }
        }
    """

    try:
        # TODO: Modify this based on your school's structure
        classes_data_table = {}

        logger.info(f"Extracted classes for {len(classes_data_table)} courses.")
        return classes_data_table
        
    except Exception as e:
        logger.error(f"Error extracting classes: {traceback.format_exc()}")
        return {}
