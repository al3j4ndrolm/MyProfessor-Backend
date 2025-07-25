from supabase import Client
from pydantic import BaseModel
from typing import Optional

TABLE_NAME = "professors"

class Professors(BaseModel):
    professor_name: str
    email: Optional[str] = None
    school: str
    department: str
    difficulty: Optional[float] = None
    rating: Optional[float] = None
    recommend: Optional[int] = None
    review_count: int


def save(supabase: Client, professors_data_list: set[tuple[str, str, str]], school: str):
    to_insert = []

    for professor_name, email, department in professors_data_list:
        # only insert if professor does not exist
        existing_professor = supabase.table(TABLE_NAME).select("*").eq("professor_name", professor_name).eq("email", email).eq("school", school).eq("department", department).execute()
        if len(existing_professor.data) == 0:
            professor = Professors(
                professor_name = professor_name,
                email = email,
                school = school,
                department = department,
                difficulty = None,
                rating = None,
                recommend = None,
                review_count = 0) 
            to_insert.append(professor.model_dump())

    # insert all professors at once
    supabase.table(TABLE_NAME).insert(to_insert).execute()