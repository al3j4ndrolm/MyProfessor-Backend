from data_fetchers.api.classes.configs import HAS_EMAIL_KEY, CLASSES_KEY, CLASS_CRN_KEY, MEETINGS_KEY, TAG_KEY, DAYS_KEY, TIME_KEY, LOCATION_KEY, AVAILABILITY_KEY

def create_professor_data(has_email: bool) -> dict:
    """
    Example of return value: {
        "has_email": False,
        "classes": [
            {
                "class_crn": "25051",
                "meetings": [
                    {
                        "tag": "CLAS",
                        "days": "MTWR···",
                        "time": "09:30 AM-10:20 AM",
                        "location": "S35"
                    }
                ]
            }
        ]
    }
    """
    return {
        HAS_EMAIL_KEY: has_email,
        CLASSES_KEY: [],
    }

def add_class_to_professor(professor_data: dict, class_data: dict):

    professor_data[CLASSES_KEY].append(class_data)

def create_class_data(class_crn = "N/A", availability = "N/A") -> dict:
    """
    Example of return value: 
                {
                    "class_crn": "25051",
                    "meetings": [
                        {
                            "tag": "CLAS",
                            "days": "MTWR···",
                            "time": "09:30 AM-10:20 AM",
                            "location": "S35"
                        }
                    ],
                    "availability": "Open"
                }
    """
    return {
            CLASS_CRN_KEY: class_crn,
            MEETINGS_KEY: [],
            AVAILABILITY_KEY: availability,
        }

def add_meeting_to_class(class_data: dict, meeting_data: dict):

    class_data[MEETINGS_KEY].append(meeting_data)

def create_meeting_data(tag = "", days = "·········", time = "", location = "") -> dict:
    """
    Example of return value: {
        "tag": "CLAS",
        "days": "MTWR···",
        "time": "09:30 AM-10:20 AM",
        "location": "S35"
    }
    """
    return {
        TAG_KEY: tag,
        DAYS_KEY: format_days(days),
        TIME_KEY: time,
        LOCATION_KEY: location
    }

def format_days(day_str):
    valid_chars = set('MTWRFSU·')
    if len(day_str) == 7 and all(c in valid_chars for c in day_str):
        return day_str  # already formatted

    all_days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    return ''.join([d if d in day_str else '·' for d in all_days])
