from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def save_courses_data(courses_data_table: dict, school_name: str):

    for department, courses in courses_data_table.items():
        data = {
            "school_name": school_name,
            "department": department,
            "data": list(courses), #from set to list to be json serializable
        }
        response = supabase.table("courses").insert(data).execute()
        print(f"Inserted {department} into courses:", response.data)



# if __name__ == "__main__":
#     school_name = "San Jose State University"
#     save_courses_data(courses_data_table, school_name)