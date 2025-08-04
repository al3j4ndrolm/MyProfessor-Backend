DAY_MAP  = {
    "Mo":"M",
    "Tu":"T",
    "We":"W",
    "Th":"R",
    "Fr":"F",
    "Sa":"S",
    "Su":"U",
    "M":"M",
    "T":"T",
    "W":"W",
    "R":"R",
    "F":"F",
    "S":"S",
    "U":"U"
    }

DAYS = ["M", "T", "W", "R", "F", "S", "U"]

def get_normalized_days(days: str) -> str:
    if days.strip() == "TBA":
        days = ""

    for key in DAY_MAP.keys():
        days = days.replace(key, DAY_MAP[key])

    return "".join(day if day in days else "·" for day in DAYS)