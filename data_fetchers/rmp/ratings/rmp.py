# External Imports
from bs4 import BeautifulSoup, Tag
import re
import jellyfish
import traceback

# Local Imports
from helpers.soup_getter import html_url_to_soup
from helpers.data import data_keys, data_creators
from data_fetchers.rmp.ratings.configs import RMP_DEFAULTS
from logger import logger

BASE_URL = "https://www.ratemyprofessors.com/search/professors/"

SIMILARITY_THRESHOLD = 0.65

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
    else:
        rmp_data[data_keys.PROFESSOR_RATING_KEY] = RMP_DEFAULTS[data_keys.PROFESSOR_RATING_KEY]
        rmp_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY] = RMP_DEFAULTS[data_keys.PROFESSOR_REVIEW_COUNT_KEY]
        rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY] = RMP_DEFAULTS[data_keys.PROFESSOR_DIFFICULTY_KEY]
        rmp_data[data_keys.PROFESSOR_RECOMMEND_KEY] = RMP_DEFAULTS[data_keys.PROFESSOR_RECOMMEND_KEY]

    del rmp_data['professor_element']
    del rmp_data['rmp_name']

    return data_creators.process_rmp_data(rmp_data)

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

    target_words = re.split(r'[\s\-\(\)\.]+', target_name)
    candidate_words = re.split(r'[\s\-\(\)\.]+', candidate_name)
    if _is_covered_by(target_words, candidate_words) or _is_covered_by(candidate_words, target_words):
        return 0.99
    
    score_target_to_candidate = _get_overall_score(target_words, candidate_words)
    score_candidate_to_target = _get_overall_score(candidate_words, target_words)
    return max(score_target_to_candidate, score_candidate_to_target)

def _is_covered_by(target_words: list[str], candidate_words: list[str]) -> bool:
    return all(word in candidate_words for word in target_words)

def _get_overall_score(words1: list[str], words2: list[str]) -> float:
    # Use Jellyfish algorithms for name similarity
    scores = []
    for word1 in words1:
        word1_scores = [_get_score(word1, word2) for word2 in words2]
        word1_score = max(word1_scores)
        scores.append(word1_score)
    return min(scores)

def _get_score(word1: str, word2: str) -> float:
    if word1 == word2:
        return 1.0
    elif word1.startswith(word2) or word2.startswith(word1):
        return 0.9
    else:
        score = jellyfish.jaro_winkler_similarity(word1, word2)
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
        logger.error(f"Error getting professor ratings for {_get_professor_name(professor_element)}: {traceback.format_exc()}")
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

"""
<a class="TeacherCard__StyledTeacherCard-syjs0d-0 eerjaA" href="/professor/2814263">
    <div class="TeacherCard__InfoRatingWrapper-syjs0d-3 kAxNBg">
        <div class="TeacherCard__NumRatingWrapper-syjs0d-2 bvYZTI">
            <div class="CardNumRating__StyledCardNumRating-sc-17t4b9u-0 cSNjdE">
                <div class="CardNumRating__CardNumRatingHeader-sc-17t4b9u-1 lhHpkk">QUALITY</div>
                <div class="CardNumRating__CardNumRatingNumber-sc-17t4b9u-2 ERCLc">4.2</div>
                <div class="CardNumRating__CardNumRatingCount-sc-17t4b9u-3 ckSFVh">42 ratings</div>
            </div>
        </div>
        <div class="TeacherCard__CardInfo-syjs0d-1 cwMOi">
            <div class="CardName__StyledCardName-sc-1gyrgim-0 gGdQEj">Andrew Oliphant</div>
            <div class="CardSchool__StyledCardSchool-sc-19lmz2k-2 irrVnX">
                <div class="CardSchool__Department-sc-19lmz2k-0 hRJPlj">Geography</div>
                <div class="CardSchool__School-sc-19lmz2k-1 bjvHvb">San Francisco State University</div>
            </div>
            <div class="CardFeedback__StyledCardFeedback-lq6nix-0 cLXvfC">
                <div class="CardFeedback__CardFeedbackItem-lq6nix-1 bqWpYz">
                    <div class="CardFeedback__CardFeedbackNumber-lq6nix-2 iHkSBk">100%</div>
                        would take again
                </div>
                <div class="VerticalSeparator-sc-1l9ngcr-0 kXhgKB"></div> 
                <div class="CardFeedback__CardFeedbackItem-lq6nix-1 bqWpYz">
                    <div class="CardFeedback__CardFeedbackNumber-lq6nix-2 iHkSBk">2.6</div>
                        level of difficulty
                </div>
            </div>
        </div>
    </div>
</a>
"""