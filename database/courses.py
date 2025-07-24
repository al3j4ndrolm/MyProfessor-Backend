from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel

class Course(BaseModel):
    school: str
    data: dict

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

courses_table: Client = create_client(url, key).table("courses")

def save_courses_data(courses_data_table: dict, school_name: str):

    courses_data_table = {dept: list(courses) for dept, courses in courses_data_table.items()}
    data = Course(school=school_name, data=courses_data_table)
<<<<<<< Updated upstream
    courses_table.insert(data.model_dump()).execute()
=======
    
    supabase.table(TABLE_NAME).insert(data.model_dump()).execute()

def get_courses_data(supabase: Client, school_name: str) -> dict:
    courses = supabase.table(TABLE_NAME).select("*").eq("school", school_name).execute()
    courses_data = courses.data[0]["data"]
    return courses_data
>>>>>>> Stashed changes
