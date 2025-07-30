import sys
from pathlib import Path
import logging
from bs4 import BeautifulSoup

# Add the project root to Python path - this must be done before any other imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Also add the current directory to handle imports when running from MyProfessor-Backend
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))

# Local imports
from helpers.data import data_creators

logger = logging.getLogger(__name__)

def get_terms(soup: BeautifulSoup) -> list[dict]:
    """
    Get the terms from the soup.
    """
    try:
        logger.debug("Fetching terms for SFSU")

        terms_fieldset = soup.find("div", id="classScheduleQuick_term", class_="radio-label-noindent")
        print("found terms fieldset")
        terms_options = terms_fieldset.find_all("div", class_="radio")
        terms_data = build_term_data_list(terms_options)
        
        logger.info(f"Fetched {len(terms_data)} terms for SFSU")
        return terms_data
    except Exception as e:
        logger.error(f"Error fetching terms for SFSU: {e}")
        return []

def build_term_data_list(terms_options) -> list[dict]:
    """
    Build the term data list.
    """
    term_data_list = []
    for term in terms_options:
        term_data = data_creators.create_term_data(term.text, term.find("input").get("value"))
        term_data_list.append(term_data)

    return term_data_list
    
if __name__ == "__main__":
    with open("tests/test_samples/sfsu/terms_test_sample.html", "r") as file:
        soup = BeautifulSoup(file, "html.parser")
        terms = get_terms(soup)
        print(terms)