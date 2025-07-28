# External Imports
from bs4 import BeautifulSoup, Tag
import re
import jellyfish

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys, data_creators
from logger import logger

BASE_URL = "https://www.ratemyprofessors.com/search/professors/"

SIMILARITY_THRESHOLD = 0.8

def get_rmp_data(professor_name: str, rmp_code: str) -> dict | None:
    """
    Example of return value:
    {
        "link": "/professor/1234567890",
        "score": 0.988,
        "rating": "4.5",
        "reviewCount": "100",
        "difficulty": "3.0",
        "recommend": "90"
    }
    """
    
    logger.debug(f"searching for '{professor_name}'...")
    soup = _search_soup(professor_name, rmp_code)
    potential_matches = _get_potential_matches(soup)
    
    if not potential_matches:
        logger.debug(f"No results found for '{professor_name}'.")
        return None
        
    rmp_data = _get_best_match_data(potential_matches, professor_name)
    if not rmp_data:
        logger.debug(f"No suitable match found for '{professor_name}'.")
        return None

    logger.debug(f"Found best match for '{professor_name}' being {rmp_data['rmp_name']}.")

    rmp_data[data_keys.PROFESSOR_LINK_KEY] = _get_link(rmp_data['professor_element'])
    # rmp_data["department"] = _get_professor_department(rmp_data['professor_element'])

    professor_ratings = _get_ratings(rmp_data['professor_element'])
    if professor_ratings:
        rmp_data.update(professor_ratings)

    del rmp_data['professor_element']
    del rmp_data['rmp_name']

    return data_creators.typed_rmp_data(rmp_data)

def _get_potential_matches(soup: BeautifulSoup) -> list[Tag]:

    ratings_holder = soup.find('div', class_=re.compile(r'^SearchResultsPage__StyledResultsWrapper'))

    if ratings_holder is None:
        logger.debug("No result section found, maybe website has changed.")
        return []

    try:
        professor_elements = ratings_holder.find_all('a', class_=re.compile(r'^TeacherCard__StyledTeacherCard'))
        return professor_elements
    except Exception as e:
        logger.error(f"Error getting professor elements: {e}")
        return []

def _get_best_match_data(professor_elements: list[Tag], professor_name: str) -> dict:
    """
    Example of return value:
    {
        "rmp_name": "Andrew Yu",
        "professor_element": <Tag>,
        "score": 0.988
    }
    """
    best_match = None
    best_similarity = 0.0
    
    for professor_element in professor_elements:

        try:
            candidate_name = _get_professor_name(professor_element)
            candidate_department = _get_professor_department(professor_element)
            similarity = _get_name_similarity(professor_name.lower(), candidate_name.lower()) 
        except Exception as e:
            logger.debug(f"Error processing professor element: {e}")
            continue

        logger.debug(f"Candidate: '{candidate_name}' - similarity: {similarity:.3f}")
        
        if similarity > best_similarity:
            best_similarity = similarity
            if similarity >= SIMILARITY_THRESHOLD:
                best_match = professor_element
                logger.debug(f"  → New best match!")
    
    if best_match is None:
        return None
    return {
        "rmp_name": _get_professor_name(best_match),
        "professor_element": best_match,
        data_keys.PROFESSOR_SCORE_KEY: round(best_similarity, 3)
    }

def _get_name_similarity(target_name: str, candidate_name: str) -> float:
    """
    Calculate similarity for names using Jellyfish algorithms.
    Uses Jaro-Winkler (best for names) and Levenshtein as fallback.
    """
    if target_name == candidate_name:
        return 1.0
    
    scores = []
    curve = 1.0

    # Check last names - if they don't match, apply heavy penalty
    target_words = target_name.split()
    candidate_words = candidate_name.split()
    
    if len(target_words) >= 2 and len(candidate_words) >= 2:

        target_last_name = target_words[-1]
        candidate_last_name = candidate_words[-1]
        scores.append(_get_lastname_score(target_last_name, candidate_last_name))

        target_first_name = target_words[0]
        candidate_first_name = candidate_words[0]
        scores.append(_get_firstname_score(target_first_name, candidate_first_name))

        curve = min(scores[0], scores[1])
    
    overall_score = _get_overall_score(target_name, candidate_name)
    scores.append(overall_score)

    return sum(scores)/len(scores)*curve

def _get_overall_score(target_name: str, candidate_name: str) -> float:
    # Clean names for comparison (remove parentheses and normalize)
    target_clean = re.sub(r'\([^)]*\)', '', target_name).strip()
    candidate_clean = re.sub(r'\([^)]*\)', '', candidate_name).strip()
    
    # Use Jellyfish algorithms for name similarity
    jellyfish_similarities = [
        jellyfish.jaro_winkler_similarity(target_name, candidate_name),
        jellyfish.jaro_winkler_similarity(target_name, candidate_clean),
        jellyfish.jaro_winkler_similarity(target_clean, candidate_name),
        jellyfish.jaro_winkler_similarity(target_clean, candidate_clean),
    ]
    
    return max(jellyfish_similarities)*0.6 + sum(jellyfish_similarities)/len(jellyfish_similarities)*0.4

def _get_lastname_score(target_last_name: str, candidate_last_name: str) -> float:
    if target_last_name == candidate_last_name:
        return 1.0
    elif target_last_name.startswith(candidate_last_name) or candidate_last_name.startswith(target_last_name):
        if len(target_last_name) == 1 or len(candidate_last_name) == 1:
            return 0.9
        else:
            return 0.5
    else:
        return 0.0

def _get_firstname_score(target_first_name: str, candidate_first_name: str) -> float:
    if target_first_name == candidate_first_name:
        return 1.0
    elif target_first_name.startswith(candidate_first_name) or candidate_first_name.startswith(target_first_name):
        return 0.9
    else:
        score = jellyfish.jaro_winkler_similarity(target_first_name, candidate_first_name)
        return score * score

def _get_ratings(professor_element: Tag) -> dict:
    """
    Example of return value:
    {
        "rating": "4.5",
        "reviewCount": "100",
        "difficulty": "3.0",
        "recommend": "90"
    }
    """
    try:
        data_holder = professor_element.find('div', class_=re.compile(r'^TeacherCard__InfoRatingWrapper'))
        rating = data_holder.find('div', class_=re.compile(r'^CardNumRating__CardNumRatingNumber')).text
        rating_count = data_holder.find('div', class_=re.compile(r'^CardNumRating__CardNumRatingCount')).text

        difficulty_and_recommend = data_holder.find_all('div', class_=re.compile(r'^CardFeedback__CardFeedbackNumber'))
        difficulty = difficulty_and_recommend[1].text.split(' ')[0]
        recommend = difficulty_and_recommend[0].text.split(' ')[0]

        return {
            data_keys.PROFESSOR_RATING_KEY: rating,
            data_keys.PROFESSOR_REVIEW_COUNT_KEY: rating_count.replace(' ratings', ''),
            data_keys.PROFESSOR_DIFFICULTY_KEY: difficulty,
            data_keys.PROFESSOR_RECOMMEND_KEY: recommend.replace('%', '')}
    except Exception as e:
        logger.error(f"Error getting professor ratings: {e}")
        return None

def _search_soup(professor_name: str, rmp_code: str) -> BeautifulSoup:
    search_url = BASE_URL + rmp_code + "?q=" + professor_name
    return html_url_to_soup(search_url)

def _get_professor_name(professor_element: Tag) -> str:
    return professor_element.find('div', class_=re.compile(r'^CardName__StyledCardName')).text

def _get_link(professor_element: Tag) -> str:
    return professor_element.get('href')

def _get_professor_department(professor_element: Tag) -> str:
    return professor_element.find('div', class_=re.compile(r'^CardSchool__Department')).text

if __name__ == "__main__":
    get_rmp_data(["Andrew Yu", "Jian Andrew Yu", "Jian Yu"], "1967")