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
        search_query = supabase.table(TABLE_NAME)\
            .select("*").eq("professor_name", professor_name)\
            .eq("email", email)\
            .eq("school", school)\
            .eq("department", department)\
            .execute()
        
        if not search_query.data:
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

def update_email(supabase: Client, professors_data_list: set[tuple[str, str, str]], school: str):
    to_update = []

    for professor_name, email, department in professors_data_list:
        
        search_query = supabase.table(TABLE_NAME)\
            .select("*").eq("professor_name", professor_name)\
            .eq("school", school)\
            .eq("department", department)\
            .execute()

        # only update if professor does not have email
        if search_query.data and search_query.data[0]["email"] is None:
            professor = Professors(
                professor_name = professor_name,
                email = email,
                school = school,
                department = department,
                difficulty = search_query.data[0]["difficulty"],
                rating = search_query.data[0]["rating"],
                recommend = search_query.data[0]["recommend"],
                review_count = search_query.data[0]["review_count"]) 
            to_update.append(professor.model_dump())

    for row in to_update:
        supabase.table(TABLE_NAME).update(row).eq("professor_name", row["professor_name"])\
            .eq("school", row["school"])\
            .eq("department", row["department"])\
            .execute()