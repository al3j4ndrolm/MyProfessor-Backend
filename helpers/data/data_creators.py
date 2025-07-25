from helpers.data import data_keys

def create_term_response_data(term_name: str, term_code: str) -> dict:
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

def create_professor_data(has_email: bool) -> dict:
    """
    Example of return value: 
    {
        "has_email": False,
        "classes": [],
    }
    """
    return {
        data_keys.HAS_EMAIL_KEY: has_email,
        data_keys.CLASSES_KEY: [],
    }

def add_class_to_professor(professor_data: dict, class_data: dict):

    professor_data[data_keys.CLASSES_KEY].append(class_data)

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

def add_meeting_to_class(class_data: dict, meeting_data: dict):

    class_data[data_keys.MEETINGS_KEY].append(meeting_data)

def create_meeting_data(tag = "", days = "·········", time = "", location = "") -> dict:
    """
    Example of return value: 
    {
        "tag": "CLAS",
        "days": "MTWR···",
        "time": "09:30 AM-10:20 AM",
        "location": "S35"
    }
    """
    return {
        data_keys.TAG_KEY: tag,
        data_keys.DAYS_KEY: format_days(days),
        data_keys.TIME_KEY: time,
        data_keys.LOCATION_KEY: location
    }

def format_days(day_str):
    valid_chars = set('MTWRFSU·')
    if len(day_str) == 7 and all(c in valid_chars for c in day_str):
        return day_str  # already formatted

    all_days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    return ''.join([d if d in day_str else '·' for d in all_days])