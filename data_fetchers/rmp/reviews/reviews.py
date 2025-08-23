from data_fetchers.rmp.reviews.configs import RMP_BASE_URL, SESSION_HEADER, RMP_GRAPHQL_URL
from data_fetchers.rmp.reviews.review_graphql import get_school_data_payload, get_professors_reviews_payload
from helpers.soup_getter import html_url_to_soup
import base64
import requests
from logger import logger
import traceback

# Public functions ------------------------------------------------------------

def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(SESSION_HEADER)
    return session

def get_reviews(professor_rmp_link: str, session: requests.Session) -> dict | None:
    reviews = _extract_reviews(professor_rmp_link, session)

    if reviews["data"]["node"]["numRatings"] == 0:
        return {}

    return reviews

# Private functions ------------------------------------------------------------
def _extract_reviews(professor_rmp_link: str, session) -> dict:
    professor_id = _get_professor_id(rmp_link=professor_rmp_link)

    try:
        payload = get_professors_reviews_payload(professor_id=professor_id)
        response = session.post(RMP_GRAPHQL_URL, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Unable to get reviews from RMP API: {e}")
        return None

def _get_professor_id(rmp_link: str) -> str:
    code = rmp_link.split("/")[-1]
    return base64.b64encode(f"Teacher-{code}".encode()).decode() # This is the format of the professor id in the RMP API

if __name__ == "__main__":
    session = get_session()
    reviews = get_reviews(professor_rmp_link="professor/89065", school_name="", session=session)
    print(reviews)