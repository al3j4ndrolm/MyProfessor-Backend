from data_fetchers.api.schedules.configs import PROFESSOR_NAME_KEY, HAS_EMAIL_KEY, CLASSES_KEY, CLASS_CRN_KEY, MEETINGS_KEY, TAG_KEY, DAYS_KEY, TIME_KEY, LOCATION_KEY, AVAILABILITY_KEY
import json

def create_professor_response_data(professor_name: str, has_email: bool) -> dict:
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

def add_class_to_professor(professor_response_data: dict, class_response_data: dict):

    professor_response_data[CLASSES_KEY].append(class_response_data)

def add_meeting_to_professor(professor_response_data: dict, meeting_response_data: dict):

    professor_response_data[CLASSES_KEY][-1][MEETINGS_KEY].append(meeting_response_data)

def create_class_response_data(class_crn = "N/A", availability = "N/A") -> dict:
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
    print(json.dumps(create_professor_response_data("John Doe", False), indent=2))