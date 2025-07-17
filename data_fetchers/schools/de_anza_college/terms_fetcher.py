# Standard library imports
from bs4 import BeautifulSoup, Tag

# Local imports
import helpers.soup_getter
from .school_config import base_url
from data_fetchers.api.terms.configs import TERM_NAME_KEY, TERM_CODE_KEY
from data_fetchers.api.terms.response import create_response_data

def fetch_terms() -> list[dict]:
    """
    Fetch the terms for De Anza College.
    """
    soup = helpers.soup_getter.html_url_to_soup(base_url)

    terms_options = locate_term_options_in_soup(soup)
    terms_data = build_term_data_list(terms_options)
    return terms_data


def locate_term_options_in_soup(soup) -> list[Tag]:
    """
    Locate the terms options in the terms fieldset.

    Example of terms_options: [
        <button type="button" class="btn btn-outline-primary" value="F2025">Fall 2025</button>,
        <button type="button" class="btn btn-outline-primary" value="W2025">Winter 2025</button>,
        <button type="button" class="btn btn-outline-primary" value="S2025">Spring 2025</button>,
        <button type="button" class="btn btn-outline-primary" value="Su2025">Summer 2025</button>
    ]
    """
    terms_fieldset = soup.find("fieldset", id="term-select")
    terms_options = terms_fieldset.find_all("button", type="button")
    return terms_options

def build_term_data_list(terms_options) -> list[dict]:
    """
    Get the refined terms data.

    Example of term_data_list: [
        {
            "term_name": "Fall 2025",
            "term_code": "F2025"
        },
        {
            "term_name": "Winter 2025",
            "term_code": "W2025"
        },
    ]
    """
    term_data_list = []
    for term in terms_options:
        term_data = create_response_data(term.text, term.get("value"))
        term_data_list.append(term_data)
    return term_data_list

if __name__ == "__main__":
    print(fetch_terms())