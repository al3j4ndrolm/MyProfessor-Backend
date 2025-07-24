from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import traceback


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

schedules_table: Client = create_client(url, key).table("classes")

def save_schedules_data(schedules_data_table: dict, school: str):
    for term, departments in schedules_data_table.items():
        for department, courses in departments.items():
            
            schedules_table.insert({
                "school": school,
                "department": department,
                "term": term,
                "data": courses
            }).execute()

