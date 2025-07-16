# Standard library imports
from bs4 import BeautifulSoup, Tag

# Local imports
import helpers.soup_getter

def fetch_terms_for_de_anza_college() -> list[dict]:
    """
    Fetch the terms for De Anza College.
    """
    school_url = "https://www.deanza.edu/schedule/"
    soup = helpers.soup_getter.html_url_to_soup(school_url)
    terms_fieldset = locate_terms_fieldset_in_soup(soup)
    terms_options = locate_terms_options_in_fieldset(terms_fieldset)
    terms_data = get_refined_terms_data(terms_options)
    return terms_data

def locate_terms_fieldset_in_soup(soup) -> Tag:
    """
    Locate the terms fieldset in the soup.
    """
    terms_fieldset = soup.find("fieldset", id="term-select")
    return terms_fieldset

def locate_terms_options_in_fieldset(terms_fieldset) -> list[Tag]:
    """
    Locate the terms options in the terms fieldset.
    """
    terms_options = terms_fieldset.find_all("button", type="button")
    return terms_options

def get_refined_terms_data(terms_options) -> list[dict]:
    """
    Get the refined terms data.
    """
    terms_data = []
    for term in terms_options:
        term_data = {
            "term_name": term.text,
            "term_code": term.get("value"),
        }
        terms_data.append(term_data)
    return terms_data

if __name__ == "__main__":
    print(fetch_terms_for_de_anza_college())