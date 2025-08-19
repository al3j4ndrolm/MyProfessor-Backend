from data_fetchers.ratings.review_configs import RMP_BASE_URL, SESSION_HEADER
from data_fetchers.ratings.graphql import get_school_data_payload, get_professors_reviews_payload
from helpers.soup_getter import html_url_to_soup
import base64
import requests

# Public functions ------------------------------------------------------------

def get_reviews(professor_rmp_link: str, school_name: str):
    url = f"{RMP_BASE_URL}{professor_rmp_link}"
    soup = html_url_to_soup(url)

    ratings_distribution = _extract_ratings_distribution(soup)
    top_tags = _extract_top_tags(soup)
    reviews = _extract_reviews(professor_rmp_link, school_name)
    return ratings_distribution, top_tags, reviews

def get_session():
    session = requests.Session()
    session.headers.update(SESSION_HEADER)
    return session

# Private functions ------------------------------------------------------------

def _extract_ratings_distribution(soup) -> dict:

    """ 
    returns:
        {'Awesome 5': '114', 'Great 4': '56', 'Good 3': '48', 'OK 2': '72', 'Awful 1': '179'}
    """

    ratings_distribution_data = {}
    ratings_distribution_holder = soup.find("ul", class_="RatingDistributionChart__MeterList-o2y7ff-0")
    ratings_distribution_list = ratings_distribution_holder.find_all("li")

    for row in ratings_distribution_list:
        rating_label = row.find("label").text.strip()
        rating_quantity = row.find("div").text.strip()
        ratings_distribution_data[rating_label] = rating_quantity

    return ratings_distribution_data

def _extract_top_tags(soup) -> list[str]:

    """ 
    returns:
        top_tags: list[str]
    """
    top_tags_holder = soup.find("div", class_="TeacherTags__TagsContainer-sc-16vmh1y-0")
    top_tags_list = top_tags_holder.find_all("span")

    top_tags = []
    for tag in top_tags_list:
        top_tags.append(tag.text.strip())

    return top_tags

def _extract_reviews(professor_rmp_link: str) -> dict:
    professor_id = _get_professor_id(rmp_link=professor_rmp_link)
    payload = get_professors_reviews_payload(professor_id=professor_id)
    response = get_session().post("https://www.ratemyprofessors.com/graphql", json=payload)
    return response.json()

def _get_school_id(school_name: str, session) -> str:
    payload = get_school_data_payload(school_name=school_name)
    response = session.post("https://www.ratemyprofessors.com/graphql", json=payload)
    school_id = response.json()["data"]["newSearch"]["schools"]["edges"][0]["node"]["id"]
    return school_id

def _base64_encode(string: str) -> str:
    return base64.b64encode(string.encode()).decode()

def _get_professor_id(rmp_link: str) -> str:
    code = rmp_link.split("/")[-1]
    return _base64_encode(f"Teacher-{code}")

