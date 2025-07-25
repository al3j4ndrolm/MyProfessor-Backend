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

def create_professor_data(email: str) -> dict:
    """
    Example of return value: 
    {
        "hasEmail": False,
        "email": "example@example.com",
        "classes": [],
    }
    """
    return {
        data_keys.HAS_EMAIL_KEY: email is not None,
        data_keys.EMAIL_KEY: email,
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

def get_professors(classes_data_table: dict) -> set[tuple[str, str, str]]:
    professors = set()
    for term_code, classes_all_departments in classes_data_table.items():
        for department, classes_per_department in classes_all_departments.items():
            for course_name, classes_per_professor in classes_per_department.items():
                for professor_name, professor_data in classes_per_professor.items():
                    professor_data_tuple = (professor_name, professor_data[data_keys.EMAIL_KEY], department)
                    professors.add(professor_data_tuple)
    return professors