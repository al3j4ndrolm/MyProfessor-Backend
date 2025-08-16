from helpers.data import data_keys

def create_term_data(term_name: str, term_code: str) -> dict:
    """
    Example of return value: {
        "term_name": "Fall 2025",
        "term_code": "F2025"
    }
    """

    return {    
        data_keys.TERM_NAME_KEY: term_name,
        data_keys.TERM_CODE_KEY: term_code,
    }

def process_term_data_list(term_data_list: list[dict]) -> list[dict]:
    """
    Sort terms by:
    1. If termCode can be cast to int, sort by that descending
    2. Otherwise, sort by termName: year descending, then season (Fall > Summer > Spring > Winter)
    
    Example of return value:
    """
    def get_sort_key(term_data):
        term_code = term_data[data_keys.TERM_CODE_KEY]
        term_name = term_data[data_keys.TERM_NAME_KEY]
        
        try:
            code_int = int(term_code)
            return (0, -code_int)
        except (ValueError, TypeError):
            return (1, _get_term_name_sort_key(term_name))
    
    sorted_term_data_list = sorted(term_data_list, key=get_sort_key)
    return sorted_term_data_list

def _get_term_name_sort_key(term_name: str) -> tuple:
    """
    Extract year and season from term name and return a sort key.
    Returns (negative_year, season_priority) for descending sort.
    
    Season priority: Fall=0, Summer=1, Spring=2, Winter=3 (lower = higher priority)
    """
    import re
    
    # Extract year from term name
    year_match = re.search(r'(\d{4})', term_name)
    if not year_match:
        # If no year found, return low priority
        return (0, 999)
    
    year = int(year_match.group(1))
    
    # Determine season priority
    term_lower = term_name.lower()
    if 'fall' in term_lower:
        season_priority = 0
    elif 'summer' in term_lower:
        season_priority = 1
    elif 'spring' in term_lower:
        season_priority = 2
    elif 'winter' in term_lower:
        season_priority = 3
    else:
        # Unknown season, give low priority
        season_priority = 999
    
    # Return negative year for descending sort, and season priority
    return (-year, season_priority)

def create_courses_data(department_name: str, courses_names: set) -> dict:
    """
    Example of return value:
    {
        "ACCT - Accounting": [
            "ACCT 64 - Payroll and Business Tax Accounting",
            "ACCT 1C - Managerial Accounting",
            ...
        ],
        "BIO - Biology": [
            "BIO 10 - Introduction to Biology",
            "BIO 11 - Introduction to Biology Lab",
            ...
        ],  
        ...
    } 
    """

    return {
        department_name: sorted(list(courses_names))
    }

def create_professor_data(email: str | None) -> dict:
    """
    Example of return value: 
    {
        "hasEmail": False,
        "classes": [],
    }
    """
    professor_data = {
            data_keys.PROFESSOR_HAS_EMAIL_KEY: email is not None,
            data_keys.PROFESSOR_CLASSES_KEY: [],
        }

    return professor_data

def create_class_data(class_crn = "N/A", availability = "N/A") -> dict:
    """
    Example of return value: 
    {
        "availability": "Open",
        "class_crn": "25051",
        "meetings": [],
    }
    """
    return {
            data_keys.CLASS_CRN_KEY: class_crn,
            data_keys.MEETINGS_KEY: [],
            data_keys.AVAILABILITY_KEY: availability,
        }

def create_meeting_data(tag = "", days = "·········", time = "", location = "") -> dict:
    """
    Example of return value: 
    {
        "tag": "",
        "days": "MTWR···",
        "time": "09:30 AM-10:20 AM",
        "location": "S35"
    }
    """
    return {
        data_keys.TAG_KEY: tag,
        data_keys.DAYS_KEY: _format_days(days),
        data_keys.TIME_KEY: time.strip(),
        data_keys.LOCATION_KEY: location.strip()
    }

def process_rmp_data(rmp_data: dict) -> dict:
    """
    Example of rmp data:
    {
        "score":0.988,
        "link":"/professor/2153406",
        "rating":"4.4",
        "reviewCount":"132",
        "difficulty":"2.7",
        "recommend":"82"
    }
    """
    review_count = _safe_int(rmp_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY])
    if review_count == 0:
        rmp_data[data_keys.PROFESSOR_RATING_KEY] = -0.1
        rmp_data[data_keys.PROFESSOR_RECOMMEND_KEY] = -1
        rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY] = 5.1
    
    return {
        data_keys.PROFESSOR_RATING_KEY: _safe_float(rmp_data[data_keys.PROFESSOR_RATING_KEY]),
        data_keys.PROFESSOR_REVIEW_COUNT_KEY: _safe_int(rmp_data[data_keys.PROFESSOR_REVIEW_COUNT_KEY]),
        data_keys.PROFESSOR_DIFFICULTY_KEY: _safe_float(rmp_data[data_keys.PROFESSOR_DIFFICULTY_KEY]),
        data_keys.PROFESSOR_RECOMMEND_KEY: _safe_int(rmp_data[data_keys.PROFESSOR_RECOMMEND_KEY]),
        data_keys.PROFESSOR_SCORE_KEY: _safe_float(rmp_data[data_keys.PROFESSOR_SCORE_KEY]),
        data_keys.PROFESSOR_LINK_KEY: rmp_data[data_keys.PROFESSOR_LINK_KEY]
    }

def create_professor_identifier(professor_name: str, professor_email: str) -> str:
    return f"{professor_name} email:{professor_email}"

def parse_professor_identifier(professor_identifier: str) -> tuple[str, str]:
    professor_name, professor_email = professor_identifier.split(" email:")
    professor_name = professor_name.strip()
    professor_email = professor_email.strip(")")
    return professor_name, professor_email

def _safe_float(value):
    """Convert value to float, return None if conversion fails"""
    if value is None or value == "" or value == "N/A":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def _safe_int(value):
    """Convert value to int, return None if conversion fails"""
    if value is None or value == "" or value == "N/A":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def _format_days(day_str):
    valid_chars = set('MTWRFSU·')
    if len(day_str) == 7 and all(c in valid_chars for c in day_str):
        return day_str  # already formatted

    all_days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    return ''.join([d if d in day_str else '·' for d in all_days])