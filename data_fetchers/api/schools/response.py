

def create_schools_data(schools_data: list[dict]) -> dict:
    schools = []
    for school in schools_data:
        schools.append(create_school_data(school["school"], school["rmp_code"], school["terms"]))
    return {"schools": schools, "broadcasts": []}

def create_school_data(school_name: str, rmp_code: str, terms: list[dict]) -> dict:
    return {
        "schoolName": school_name,
        "rmpCode": rmp_code,
        "terms": terms,
        "notifications": {"text": ""}
    }