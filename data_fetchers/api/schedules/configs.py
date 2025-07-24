
# Schedules configs
HAS_EMAIL_KEY = "hasEmail"
CLASSES_KEY = "classes"
CLASS_CRN_KEY = "classCrn"
MEETINGS_KEY = "meetings"
TAG_KEY = "tag"
DAYS_KEY = "days"
TIME_KEY = "time"
LOCATION_KEY = "location"
AVAILABILITY_KEY = "availability"

"""
Example of return value:
{
    "PHYS": {
        "PHYS 101": {
            "John Doe": {
                "hasEmail": False,
                "classes": [
                    {
                        "classCrn": "25051",
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
            },
            ...
        },
        ...
    },
    "MATH": {
        ...
    }
}
"""