from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel

class Schedule(BaseModel):
    school: str
    department: str
    term: str
    data: dict

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

schedules_table: Client = create_client(url, key).table("classes")

def save_schedules_data(schedules_data_table: dict, school: str):
    for term, schedules_all_departments in schedules_data_table.items():
        for department, schedules_per_department in schedules_all_departments.items():
            
            schedule = Schedule(school=school, department=department, term=term, data=schedules_per_department)
            schedules_table.insert(schedule.model_dump()).execute()

