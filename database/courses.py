from supabase import create_client, Client
import os
from dotenv import load_dotenv


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

<<<<<<< HEAD
courses_table: Client = create_client(url, key).table("courses")
=======
supabase: Client = create_client(url, key)
>>>>>>> 2bc1b5850e62bd7a55151af3b18dce93e85c7290

def save_courses_data(courses_data_table: dict, school_name: str):

    courses_data_table = {dept: list(courses) for dept, courses in courses_data_table.items()}
    data = {
        "school_name": school_name,
        "data": courses_data_table,
    }
<<<<<<< HEAD
    courses_table.insert(data).execute()
=======
    supabase.table("courses").insert(data).execute()
>>>>>>> 2bc1b5850e62bd7a55151af3b18dce93e85c7290

# if __name__ == "__main__":    
#     school_name = "San Jose State University"
#     save_courses_data(courses_data_table, school_name)