from data_fetchers.rmp.reviews.configs import SESSION_HEADER, RMP_GRAPHQL_URL
from data_fetchers.rmp.reviews.review_graphql import get_professors_reviews_payload
import base64
import requests
from logger import logger

# Public functions ------------------------------------------------------------

def setup_request_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(SESSION_HEADER)
    return session

def get_reviews(professor_rmp_link: str, session: requests.Session) -> list[dict] | None:
    result = _extract_reviews(professor_rmp_link, session)

    if not result["data"]["node"] or "numRatings" not in result["data"]["node"]:
        logger.warning(f"Unexpected review json: {result["data"]} for professor {professor_rmp_link}")
        return {}
    if result["data"]["node"]["numRatings"] == 0:
        return {}

    edges = result['data']['node']['ratings']['edges']
    reviews = [edge['node'] for edge in edges]
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
    # This is the format of the professor id in the RMP API
    return base64.b64encode(f"Teacher-{code}".encode()).decode()

if __name__ == "__main__":
    session = setup_request_session()
    reviews = get_reviews(professor_rmp_link="professor/89065", school_name="", session=session)
    print(reviews)