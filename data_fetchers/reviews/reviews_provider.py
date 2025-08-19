from data_fetchers.ratings.review_configs import RMP_BASE_URL, SESSION
from data_fetchers.ratings.graphql import get_school_data_payload, get_professors_reviews_payload
from helpers.soup_getter import html_url_to_soup
import base64


def get_reviews(professor_rmp_link: str, school_name: str):

    url = f"{RMP_BASE_URL}{professor_rmp_link}"
    soup = html_url_to_soup(url)

    ratings_distribution = extract_ratings_distribution(soup)
    top_tags = extract_top_tags(soup)
    reviews = extract_reviews(professor_rmp_link, school_name)
    
    return reviews

def extract_ratings_distribution(soup) -> dict:

    """ 
    Extracts the ratings distribution from the RMP page of the professor.

    returns:
        ratings_distribution_data: dict
            key: rating label
            value: rating quantity

    example:
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

def extract_top_tags(soup) -> list[str]:

    """ 
    Extracts the top tags from the RMP page of the professor.

    returns:
        top_tags: list[str]
    """

    top_tags_holder = soup.find("div", class_="TeacherTags__TagsContainer-sc-16vmh1y-0")
    top_tags_list = top_tags_holder.find_all("span")

    top_tags = []

    for tag in top_tags_list:
        top_tags.append(tag.text.strip())

    return top_tags

def extract_reviews(professor_rmp_link: str, school_name: str) -> int:

    """ 
    Extracts the reviews from the RMP page of the professor.

    returns:
        reviews: list[dict]
    """

    school_id = _get_school_id(school_name=school_name)
    professor_id = _get_professor_id(rmp_link=professor_rmp_link)
    payload = get_professors_reviews_payload(professor_id=professor_id)

    response = SESSION.post("https://www.ratemyprofessors.com/graphql", json=payload)
    print(response.json())

def _get_school_id(school_name: str) -> str:
    payload = get_school_data_payload(school_name=school_name)
    response = SESSION.post("https://www.ratemyprofessors.com/graphql", json=payload)
    school_id = response.json()["data"]["newSearch"]["schools"]["edges"][0]["node"]["id"]
    return school_id

def _base64_encode(string: str) -> str:
    return base64.b64encode(string.encode()).decode()

def _get_professor_id(rmp_link: str) -> str:
    code = rmp_link.split("/")[-1]
    return _base64_encode(f"Teacher-{code}")