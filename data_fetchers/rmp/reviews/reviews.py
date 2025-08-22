from data_fetchers.rmp.reviews.configs import RMP_BASE_URL, SESSION_HEADER, RMP_GRAPHQL_URL
from data_fetchers.rmp.reviews.review_graphql import get_school_data_payload, get_professors_reviews_payload
from helpers.soup_getter import html_url_to_soup
import base64
import requests
from logger import logger

# Public functions ------------------------------------------------------------

def get_session():
    session = requests.Session()
    session.headers.update(SESSION_HEADER)
    return session

# TODO: Remove school_name parameter if not needed for AI Summary
def get_reviews(professor_rmp_link: str, school_name: str, session):
    url = f"{RMP_BASE_URL}{professor_rmp_link}"
    soup = html_url_to_soup(url)

    ratings_distribution = _extract_ratings_distribution(soup)
    top_tags = _extract_top_tags(soup)

    if ratings_distribution and top_tags:
        reviews = _extract_reviews(professor_rmp_link, session)
    else:
        return None

    return (ratings_distribution, top_tags, reviews)

# TODO: Optional approach to fetch professor data from RMP API (DELETE if needed)
def get_school_id(school_name: str, session) -> str | None:
    payload = get_school_data_payload(school_name=school_name)
    response = session.post(RMP_GRAPHQL_URL, json=payload)

    try:
        return response.json()["data"]["newSearch"]["schools"]["edges"][0]["node"]["id"]
    except Exception as e:
        logger.error(f"Unable to get school id from RMP API: {e}")
        return None

# Private functions ------------------------------------------------------------

def _extract_ratings_distribution(soup) -> dict:

    """ 
    Example of return value:
        {'Awesome 5': '114', 'Great 4': '56', 'Good 3': '48', 'OK 2': '72', 'Awful 1': '179'}
    """

    ratings_distribution_data = {}
    ratings_distribution_holder = soup.find("ul", class_="RatingDistributionChart__MeterList-o2y7ff-0")

    try:
        ratings_distribution_list = ratings_distribution_holder.find_all("li")
    except:
        return {}

    for row in ratings_distribution_list:
        rating_label = row.find("label").text.strip()
        rating_quantity = row.find("div").text.strip()
        ratings_distribution_data[rating_label] = rating_quantity

    return ratings_distribution_data

def _extract_top_tags(soup) -> list[str]:

    """ 
    Example of return value:
        ['Easy', 'Helpful', 'Smart', 'Interesting']
    """
    top_tags_holder = soup.find("div", class_="TeacherTags__TagsContainer-sc-16vmh1y-0")

    try:
        top_tags_list = top_tags_holder.find_all("span")
    except:
        return []

    top_tags = []
    for tag in top_tags_list:
        top_tags.append(tag.text.strip())

    return top_tags

def _extract_reviews(professor_rmp_link: str, session) -> dict:
    professor_id = _get_professor_id(rmp_link=professor_rmp_link)
    payload = get_professors_reviews_payload(professor_id=professor_id)

    
    response = session.post(RMP_GRAPHQL_URL, json=payload)
    return response.json()

def _get_professor_id(rmp_link: str) -> str:
    code = rmp_link.split("/")[-1]
    return _base64_encode(f"Teacher-{code}")

# TODO: if this function will not be used more than one time, we don't need to wrap this
def _base64_encode(string: str) -> str:
    return base64.b64encode(string.encode()).decode()

