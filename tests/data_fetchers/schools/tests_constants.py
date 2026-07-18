import re

SEASON_CODE_MAP = {
    "Spring": "S",
    "Summer": "M",
    "Fall": "F",
    "Winter": "W",
}

COMMON_DEPARTMENTS = {
    "ANTH": "Anthropology",
    "CHEM": "Chemistry",
    "MATH": "Mathematics",
}

COURSE_ENTRY_PATTERN = re.compile(r"^(\S+(?:\s+\S+)+) - (.+)$")

TEST_DEPARTMENT_CODE = "MATH"
