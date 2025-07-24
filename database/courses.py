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
    courses_table.insert(data.model_dump()).execute()

# if __name__ == "__main__":    
#     school_name = "San Jose State University"
#     save_courses_data(courses_data_table, school_name)