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

def create_professor_data(email: str | None) -> dict:
    """
    Example of return value: 
    {
        "hasEmail": False,
        "email": "example@example.com",
        "classes": [],
    }
    """
    professor_data = {
            data_keys.PROFESSOR_HAS_EMAIL_KEY: email is not None,
            data_keys.PROFESSOR_CLASSES_KEY: [],
        }
    if email:
        professor_data[data_keys.PROFESSOR_EMAIL_KEY] = email
    return professor_data

def add_class_to_professor(professor_data: dict, class_data: dict):

    professor_data[data_keys.PROFESSOR_CLASSES_KEY].append(class_data)

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

def get_professors(classes_data_table: dict) -> dict:
    """
    classes_data_table is:
        a dict of term_code 
            to dict of department 
                to dict of course_name 
                    to dict of professor_name to professor_data
    """
    professors_by_department = {}
    for term_code, classes_all_departments in classes_data_table.items():
        for department, classes_per_department in classes_all_departments.items():
            
            professors_by_department[department] = professors_by_department.get(department, {})
            for course_name, classes_per_course in classes_per_department.items():
                for professor_name, professor_data in classes_per_course.items():
                    email = professor_data[data_keys.PROFESSOR_EMAIL_KEY]
                    professors_by_department[department][(professor_name, email)] = {
                            data_keys.PROFESSOR_NAME_KEY: professor_name,
                            data_keys.PROFESSOR_EMAIL_KEY: email,
                            data_keys.PROFESSOR_DEPARTMENT_KEY: department
                        }

    return professors_by_department

def get_professor_from_rmp_data(rmp_data: dict) -> dict:
    """
    Example of rmp data:
    {
        "Jian Andrew Yu":{
            "score":0.988,
            "professor_name":"Jian Andrew Yu",
            "link":"/professor/2153406",
            "department":"Mathematics & Statistics",
            "rating":"4.4",
            "reviews_count":"132",
            "difficulty":"2.7",
            "recommend":"82"
        },
        ...
    }
    """
    
    def safe_float(value):
        """Convert value to float, return None if conversion fails"""
        if value is None or value == "" or value == "N/A":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def safe_int(value):
        """Convert value to int, return None if conversion fails"""
        if value is None or value == "" or value == "N/A":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    return {
        data_keys.PROFESSOR_NAME_KEY: rmp_data["professor_name"],
        # data_keys.PROFESSOR_EMAIL_KEY: rmp_data["email"],
        # data_keys.PROFESSOR_DEPARTMENT_KEY: rmp_data["department"],
        data_keys.PROFESSOR_RATING_KEY: safe_float(rmp_data["rating"]),
        data_keys.PROFESSOR_REVIEW_COUNT_KEY: safe_int(rmp_data["reviews_count"]),
        data_keys.PROFESSOR_DIFFICULTY_KEY: safe_float(rmp_data["difficulty"]),
        data_keys.PROFESSOR_RECOMMEND_KEY: safe_int(rmp_data["recommend"]),
        data_keys.PROFESSOR_SCORE_KEY: safe_float(rmp_data["score"]),
        data_keys.PROFESSOR_LINK_KEY: rmp_data["link"]
    }