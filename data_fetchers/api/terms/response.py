from data_fetchers.api.terms.configs import TERM_NAME_KEY, TERM_CODE_KEY, PROFESSOR_NAME_KEY, HAS_EMAIL_KEY, CLASSES_KEY, CLASS_CRN_KEY, MEETINGS_KEY, TAG_KEY, DAYS_KEY, TIME_KEY, LOCATION_KEY, AVAILABILITY_KEY


def create_terms_response_data(term_name, term_code) -> dict:
    """
    Example of return value: {
        "term_name": "Fall 2025",
        "term_code": "F2025"
    }
    """

    return {
        TERM_NAME_KEY: term_name,
        TERM_CODE_KEY: term_code,
    }

def create_classes_response_data(class_crn = "N/A", availability = "N/A", days = "N/A", time = "N/A", location = "N/A", tag = "CLAS") -> dict:
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
                    ]
                }
    """
    return {
            CLASS_CRN_KEY: class_crn,
            MEETINGS_KEY: [create_meeting_data(tag, days, time, location)],
            AVAILABILITY_KEY: availability,
        }

def create_meeting_data(tag = "N/A", days = "N/A", time = "N/A", location = "N/A") -> dict:
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
        DAYS_KEY: days,
        TIME_KEY: time,
        LOCATION_KEY: location
    }

if __name__ == "__main__":
    print(create_terms_response_data("Fall 2025", "F2025"))