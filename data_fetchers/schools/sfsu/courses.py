# Standard library imports
import logging

# Third Party Imports
import time, requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def update_courses_set_per_department(department_code: str, term_code: str, courses_set: set) -> set:
    """
    Example of return value:
    {
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        ...
    }
    """
    session = requests.Session()
    # 1) prime your session with the filters
    session.get(
        "https://webapps.sfsu.edu/public/classservices/classsearch/results",
        params={
            "searchFor":     department_code,   # ← your department code
            "term":          term_code,
            "classCategory": "REG",
        }
    )

    # 2) now fetch the JSON (timestamp only matters to bust cache)
    r = session.get(
        "https://webapps.sfsu.edu/public/classservices/searchresultsjson",
        params={"_": int(time.time() * 1000)}
    )

    data = r.json()
    # ———————————
    # 3) turn each aaData row into a nice dict
    for row in data["aaData"]:
        # row[0] is the <a>HTML, row[1] = Type, row[2] = Title, etc.
        soup = BeautifulSoup(row[0], "html.parser")
        a    = soup.find("a")
        courses_set.add(a.text.strip().split(" [")[0] + " - " + row[2])
    
    return courses_set
