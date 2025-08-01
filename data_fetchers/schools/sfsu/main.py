import sys
import os
import time
import requests

# Add the project root to the Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logger import logger

def get_session_data(department_code: str, term_code: str):

    """
    Example of return value:
    {
        "aaData": [
            [
                "<a>PHYS 200 [01]</a>",
                "REG",
                "Physics 200",
                "3",
                "1",
                "1",
                "1",
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
        return data
    except Exception as e:
        logger.error(f"Error getting data for {department_code} set per term {term_code}: {e}")
        return {}