# Standard library imports
from logger import logger

# Third Party Imports
import time, requests
from bs4 import BeautifulSoup

# we are going to pass a list of department codes and a term code to update the courses set
def update_courses_set_per_term(department_code: str, term_code: str, courses_set: set) -> set:
    """
    Example of return value:
    {
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        ...
    }
    """
    
    try:
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
    except Exception as e:
        logger.error(f"Error getting session for {department_code} set per term {term_code}: {e}")

    # 2) now fetch the JSON (timestamp only matters to bust cache)
    try:
        r = session.get(
            "https://webapps.sfsu.edu/public/classservices/searchresultsjson",
            params={"_": int(time.time() * 1000)}
        )
    except Exception as e:
        logger.error(f"Error getting JSON for {department_code} set per term {term_code}: {e}")

    try:
        data = r.json()
        # ———————————
        # 3) turn each aaData row into a nice dict
        for row in data["aaData"]:
            # row[0] is the <a>HTML, row[1] = Type, row[2] = Title, etc.
            soup = BeautifulSoup(row[0], "html.parser")
            a    = soup.find("a")
            courses_set.add(a.text.strip().split(" [")[0] + " - " + row[2])
    except Exception as e:
        logger.error(f"Error getting data for {department_code} set per term {term_code}: {e}")
    
    return courses_set
