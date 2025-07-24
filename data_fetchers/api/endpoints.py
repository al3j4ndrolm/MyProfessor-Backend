from data_fetchers.api.schools.response import create
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@router.get("/schools")
def schools_endpoint():
    return create(supabase)

# @router.get("/courses")
# def courses(
#     school_name: str = None,
#     term: str = None,
#     department: str = None
# ):
#     if school_name is None or term is None or department is None:
#         raise HTTPException(status_code=400, detail="Missing required parameters")
#     else:
#         courses_data = get_courses_data(school_name, term, department)
#         return courses_data

# @router.get("/classes")
# def classes(
#     school_name: str = None,
#     term: str = None,
#     department: str = None
# ):
#     if school_name is None or term is None or department is None:
#         raise HTTPException(status_code=400, detail="Missing required parameters")
#     else:
#         classes_data = get_classes_data(school_name, term, department)
#         return classes_data


app.include_router(router)
